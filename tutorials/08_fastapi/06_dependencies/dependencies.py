from typing import Annotated

from fastapi import Depends, Query


class Database:
    """模拟数据库连接。"""

    def __init__(self, name: str = "sqlite"):
        self.name = name


def get_db() -> Database:
    """依赖函数：创建数据库连接。"""
    db = Database(name="main_db")
    try:
        yield db
    finally:
        # 这里可以关闭数据库连接
        pass


class CommonQueryParams:
    """通用查询参数依赖类。"""

    def __init__(
        self,
        q: Annotated[str | None, Query(max_length=50)] = None,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(le=100)] = 10,
    ):
        self.q = q
        self.skip = skip
        self.limit = limit


db_session = Annotated[Database, Depends(get_db)]
