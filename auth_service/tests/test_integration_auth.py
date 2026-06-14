import asyncio
import pytest

from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db import base
from app.db.session import get_db
from app.core.config import settings
from app.main import app as fastapi_app


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture()
async def async_app():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)

    async def get_test_db():
        async with async_session() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = get_test_db

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_login_me_flow(async_app: FastAPI):
    transport = ASGITransport(app=async_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # register
        resp = await ac.post("/auth/register", json={"email": "a@example.com", "password": "pass"})
        assert resp.status_code == 200
        user = resp.json()
        assert user["email"] == "a@example.com"

        # login
        resp = await ac.post(
            "/auth/login",
            data={"username": "a@example.com", "password": "pass"},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        # me
        resp = await ac.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        me = resp.json()
        assert me["email"] == "a@example.com"


@pytest.mark.asyncio
async def test_negative_cases(async_app: FastAPI):
    transport = ASGITransport(app=async_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # register first
        resp = await ac.post("/auth/register", json={"email": "dup@example.com", "password": "p"})
        assert resp.status_code == 200

        # duplicate registration
        resp = await ac.post("/auth/register", json={"email": "dup@example.com", "password": "p"})
        assert resp.status_code == 409

        # login wrong password
        resp = await ac.post(
            "/auth/login",
            data={"username": "dup@example.com", "password": "wrong"},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

        # /me without token
        resp = await ac.get("/auth/me")
        assert resp.status_code == 401
