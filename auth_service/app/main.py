from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router as router
from app.core.config import settings
from app.db import base
from app.db.session import engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Auth Service started")

    # ensure database tables exist
    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)

    yield
    print("Auth Service stopped")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }