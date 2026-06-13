from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Auth Service started")
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