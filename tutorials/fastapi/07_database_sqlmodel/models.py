from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    """英雄数据模型。"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None


class HeroCreate(SQLModel):
    """创建英雄请求模型。"""

    name: str
    secret_name: str
    age: int | None = None


class HeroPublic(SQLModel):
    """返回英雄响应模型。"""

    id: int
    name: str
    secret_name: str
    age: int | None = None
