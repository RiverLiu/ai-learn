from typing import Annotated

from fastapi import Depends, FastAPI

from dependencies import CommonQueryParams, Database, db_session

app = FastAPI()


@app.get("/items/")
def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    """使用类依赖实现通用分页查询。"""
    return {
        "q": commons.q,
        "skip": commons.skip,
        "limit": commons.limit,
    }


@app.get("/users/")
def read_users(
    db: db_session,
    q: str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    """使用函数依赖注入数据库会话。"""
    return {
        "q": q,
        "skip": skip,
        "limit": limit,
        "db": db.name,
    }
