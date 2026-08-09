from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """用户表模型。"""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    full_name: str | None = None
    hashed_password: str
    disabled: bool = False

    todos: list["Todo"] = Relationship(back_populates="owner")


class Todo(SQLModel, table=True):
    """待办事项表模型。"""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = False
    owner_id: int = Field(foreign_key="user.id")

    owner: User = Relationship(back_populates="todos")
