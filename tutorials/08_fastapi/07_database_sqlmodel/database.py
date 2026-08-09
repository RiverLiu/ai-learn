from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# 使用 SQLite 文件数据库，便于观察
sqlite_url = "sqlite:///./heroes.db"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """创建所有表。"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """获取数据库会话依赖。"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
