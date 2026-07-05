import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，从环境变量读取。"""

    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite:///./app.db"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"启动应用，调试模式: {settings.debug}")
    yield
    print("关闭应用")


app = FastAPI(
    title="Production Ready API",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {
        "message": "Hello from production ready API",
        "debug": settings.debug,
        "database_url": settings.database_url,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
