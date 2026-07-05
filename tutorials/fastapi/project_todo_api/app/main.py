from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth, todos, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Todo API",
    description="一个使用 FastAPI + SQLModel + JWT 的待办事项 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户"])
app.include_router(todos.router, prefix="/todos", tags=["待办事项"])


@app.get("/")
def read_root():
    return {"message": "欢迎使用 Todo API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
