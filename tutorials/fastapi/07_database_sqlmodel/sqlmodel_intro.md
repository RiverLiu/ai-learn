# SQLModel 简介

本章示例用 [SQLModel](https://sqlmodel.tiangolo.com/) 做数据库 CRUD。这个文件专门讲清楚 **SQLModel 是什么、解决了什么问题、核心概念，以及它和 SQLAlchemy、Pydantic、FastAPI 的关系**。

## 1. SQLModel 是什么

SQLModel 是由 FastAPI 作者 Sebastián Ramírez（Tiangolo）开源的 Python 库。它把两件东西拼在了一起：

- **[SQLAlchemy](https://www.sqlalchemy.org/)**：Python 最流行的 ORM，负责把 Python 类映射成数据库表、执行 SQL、管理事务。
- **[Pydantic](https://docs.pydantic.dev/)**：Python 最流行的数据校验库，负责把 JSON / 字典转成类型安全的对象、做字段校验和序列化。

在 SQLModel 出现之前，写 FastAPI + 数据库通常会写两套模型：

```python
# SQLAlchemy 表模型
class Hero(Base):
    __tablename__ = "hero"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

# Pydantic 请求/响应模型
class HeroCreate(BaseModel):
    name: str

class HeroPublic(BaseModel):
    id: int
    name: str
```

字段几乎一样，却要维护三份代码。SQLModel 的想法是：**用同一个类，既能描述数据库表，又能做 API 校验**。

## 2. 一个类，两种身份

SQLModel 的核心设计非常简洁：

```python
from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = None
```

- 当 `table=True` 时，这个类是**数据库表模型**，底层会生成 SQLAlchemy 的 `Table` 定义。
- 当不写 `table=True` 时，这个类就是**纯 Pydantic 模型**，用于 FastAPI 的请求体校验或响应序列化。

所以同一个项目里通常有三层模型：

| 模型 | 作用 | 是否 `table=True` |
| --- | --- | --- |
| `Hero` | 数据库表，存持久化数据 | ✅ 是 |
| `HeroCreate` | 创建请求体校验（入参） | ❌ 否 |
| `HeroPublic` | 响应序列化（出参） | ❌ 否 |

```python
class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: int | None = None


class HeroPublic(SQLModel):
    id: int
    name: str
    secret_name: str
    age: int | None = None
```

> 为什么不直接把 `Hero` 当响应模型用？因为 `Hero` 的 `id` 在创建前是 `None`，而且未来表模型里可能包含密码、内部状态等不想暴露给前端的字段。分层是为了**最小暴露原则**。

## 3. `Field()` 的作用

`Field()` 来自 SQLModel/Pydantic，用来给字段加配置：

```python
id: int | None = Field(default=None, primary_key=True)
name: str = Field(index=True)
age: int | None = None
```

常见参数：

| 参数 | 含义 |
| --- | --- |
| `default` / `default_factory` | 默认值 |
| `primary_key=True` | 主键；通常配合 `id: int | None = Field(default=None, primary_key=True)` 让数据库自增 |
| `index=True` | 给该字段建索引，加快查询 |
| `nullable=False`（默认） | 数据库字段不允许 NULL；`int | None` 会推导为 `nullable=True` |
| `foreign_key="team.id"` | 外键关联 |
| `sa_column=Column(...)` | 透传底层 SQLAlchemy 的 `Column`，用于高级类型 |

## 4. 数据库引擎与会话

SQLModel 复用了 SQLAlchemy 的引擎和会话机制：

```python
from sqlmodel import create_engine, Session, SQLModel

sqlite_url = "sqlite:///./heroes.db"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

# 创建所有表
SQLModel.metadata.create_all(engine)

# 创建会话
with Session(engine) as session:
    hero = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    session.add(hero)
    session.commit()       # 提交事务
    session.refresh(hero)  # 获取数据库生成的 id
    print(hero.id)
```

常用会话操作：

| 操作 | 作用 |
| --- | --- |
| `session.add(obj)` | 把对象加入会话，等待提交 |
| `session.commit()` | 提交事务，真正写入数据库 |
| `session.refresh(obj)` | 把数据库生成的字段（如自增 id）刷新到对象 |
| `session.exec(statement)` | 执行 `select(...)` 等 SQLModel 语句 |
| `session.delete(obj)` | 标记删除，需再 `commit()` |

## 5. 查询语句

SQLModel 使用 SQLAlchemy 风格的 `select`：

```python
from sqlmodel import select

statement = select(Hero).where(Hero.name == "Deadpond")
heroes = session.exec(statement).all()

# 分页
statement = select(Hero).offset(skip).limit(limit)
heroes = session.exec(statement).all()

# 统计总数
from sqlalchemy import func
statement = select(func.count()).select_from(Hero)
total = session.exec(statement).one()
```

`select()`、`where()`、`offset()`、`limit()` 都返回一个**查询对象**，不会立即查数据库；真正执行发生在 `session.exec(statement)`。

## 6. 与 FastAPI 集成

SQLModel 和 FastAPI 是“一家人”，配合非常自然：

```python
from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import Session

app = FastAPI()
SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

- `hero: HeroCreate`：FastAPI 自动用 Pydantic 校验请求体。
- `session: SessionDep`：每个请求拿到独立的数据库会话，请求结束自动关闭。
- `response_model=HeroPublic`：返回对象会被序列化成 `HeroPublic`，隐藏内部字段。

## 7. 关系（Relationship）

SQLModel 也支持关系，例如一个英雄属于一个团队：

```python
class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")

    team: Team | None = Relationship(back_populates="heroes")
```

> 关系查询会触发懒加载（lazy loading），在 API 里要特别注意 N+1 问题。生产环境通常用 `selectinload` 或手动 `join`。

## 8. 迁移

SQLModel **不内置迁移工具**。`SQLModel.metadata.create_all(engine)` 只适合开发环境快速建表。

生产环境请配合 Alembic（SQLAlchemy 官方迁移工具）：

```bash
pip install alembic
alembic init alembic
```

Alembic 的迁移脚本可以直接识别 SQLModel 定义的表结构。

## 9. 常见误区

| 误区 | 正解 |
| --- | --- |
| `table=True` 和纯 Pydantic 模型混用 | 表模型用于数据库，请求/响应模型用于 API，字段再像也不要直接复用 |
| `id` 不设默认值 | 自增主键应写 `id: int | None = Field(default=None, primary_key=True)`，否则插入时会报错 |
| SQLite 多线程报错 | SQLite 文件库默认不允许跨线程，加 `connect_args={"check_same_thread": False}` |
| 把表模型直接返回给前端 | 表模型可能包含敏感字段；用 `response_model` 指定 `HeroPublic` 等脱敏模型 |
| 用 `table=True` 的模型做请求校验 | 可以，但会把 `id` 等数据库字段也暴露给请求体，通常不推荐 |

## 10. SQLModel vs SQLAlchemy vs Pydantic

| 能力 | SQLAlchemy | Pydantic | SQLModel |
| --- | --- | --- | --- |
| ORM / 数据库映射 | ✅ | ❌ | ✅（底层 SQLAlchemy） |
| 数据校验 | ⚠️ 较弱 | ✅ 强 | ✅（Pydantic v2） |
| FastAPI 请求校验 | 需额外包 | ✅ 原生 | ✅ 原生 |
| 类型提示体验 | 较老 | 好 | 好 |
| 学习曲线 | 陡峭 | 平缓 | 平缓 |

SQLModel 不是替代 SQLAlchemy，而是**在 SQLAlchemy 之上加了一层 Pydantic 风格的语法糖**。当你需要 SQLAlchemy 的高级功能（CTE、复杂 join、事件监听）时，完全可以直接写 SQLAlchemy。

## 11. 总结

- SQLModel = SQLAlchemy（数据库） + Pydantic（校验）。
- 一个类通过 `table=True` 控制它是“数据库表”还是“普通数据模型”。
- 推荐分层：`Hero`（表）、`HeroCreate`（入参）、`HeroPublic`（出参）。
- 查询、引擎、会话、迁移都继承自 SQLAlchemy 生态。
- 和 FastAPI 配合时，请求体校验、依赖注入、响应序列化开箱即用。

如果你想进一步练习，可以尝试：

1. 给 `Hero` 增加一个 `team_id` 外键，实现英雄与团队的一对多关系。
2. 把本章的 offset 分页改成带总条数的 `Page` 响应。
3. 用 Alembic 给现有表加一列 `created_at`，体验一次真实的数据库迁移。
