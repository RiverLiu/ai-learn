from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

sqlite_url = "sqlite:///./todo.db"
engine = create_engine(
    sqlite_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
