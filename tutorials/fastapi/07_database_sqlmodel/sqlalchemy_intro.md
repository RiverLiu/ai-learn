# SQLAlchemy 简介

SQLModel 的底层是 SQLAlchemy，因此理解 SQLAlchemy 的核心概念对学习 SQLModel、排查数据库问题至关重要。这个文件系统介绍 SQLAlchemy 是什么、怎么用，以及它与 SQLModel 的关系。

## 1. SQLAlchemy 是什么

[SQLAlchemy](https://www.sqlalchemy.org/) 是 Python 生态里历史最悠久、功能最全面的数据库工具集，分为两大使用模式：

| 模式 | 名称 | 特点 |
| --- | --- | --- |
| ORM 模式 | Object Relational Mapping | 把 Python 类映射成数据库表，用对象操作记录 |
| Core 模式 | SQL Expression Language | 用 Python 表达式拼 SQL，不依赖类映射 |

SQLAlchemy 支持几乎所有关系型数据库：SQLite、PostgreSQL、MySQL、MariaDB、SQL Server、Oracle 等。

## 2. 为什么需要 SQLAlchemy

直接写原始 SQL 的问题：

- 字符串拼接容易引入 SQL 注入。
- 不同数据库的 SQL 方言有差异（如 `LIMIT` vs `TOP`）。
- 手写连接池、事务、结果映射繁琐且容易出错。

SQLAlchemy 解决这些问题的方式：

- **参数化查询**：自动转义，防止 SQL 注入。
- **数据库无关的表达式层**：同一套 Python 代码可切换数据库后端。
- **连接池与事务管理**：内置连接复用和自动回滚。
- **ORM**：把查询结果自动映射成 Python 对象。

## 3. 核心概念

### 3.1 Engine（引擎）

Engine 是 SQLAlchemy 与数据库之间的连接工厂，负责维护连接池。

```python
from sqlalchemy import create_engine

# SQLite 内存数据库
engine = create_engine("sqlite:///:memory:", echo=True)

# SQLite 文件数据库
engine = create_engine("sqlite:///./app.db")

# PostgreSQL
engine = create_engine("postgresql+psycopg2://user:pass@localhost/dbname")
```

`echo=True` 会把生成的 SQL 打印到控制台，学习和调试时非常有用。

### 3.2 Connection（连接）

Connection 代表一次数据库连接，使用完要关闭。

```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name FROM hero"))
    for row in result:
        print(row.id, row.name)
```

### 3.3 Session（会话）

Session 是 ORM 模式下的工作单元（Unit of Work），它跟踪对象状态、管理事务。

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    hero = Hero(name="Deadpond")
    session.add(hero)
    session.commit()
```

Session 里的对象有三种状态：

| 状态 | 说明 |
| --- | --- |
| Transient（游离） | 刚创建，未加入 Session |
| Pending（挂起） | 已 `add()`，等待 `commit()` |
| Persistent（持久） | 已提交到数据库，Session 能跟踪它的变化 |
| Detached（分离） | Session 关闭后，对象仍在内存，但不再被跟踪 |

### 3.4 Metadata、Table 与 Mapper

SQLAlchemy 用 `MetaData` 管理所有表定义：

```python
from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

hero_table = Table(
    "hero",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, index=True),
    Column("secret_name", String),
)

# 创建表
metadata.create_all(engine)
```

ORM 模式下，用 `declarative_base` 或 `DeclarativeBase` 把类和表绑定：

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Hero(Base):
    __tablename__ = "hero"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    secret_name: Mapped[str]
```

> `Mapped[int]` 和 `mapped_column()` 是 SQLAlchemy 2.0 推荐的类型注解写法，SQLModel 底层也沿用了这套机制。

### 3.5 表达式语言

SQLAlchemy 允许用 Python 表达式写 SQL：

```python
from sqlalchemy import select, insert, update, delete

# SELECT
stmt = select(Hero).where(Hero.age > 18).order_by(Hero.name)

# INSERT
stmt = insert(Hero).values(name="Spider-Boy", secret_name="Pedro")

# UPDATE
stmt = update(Hero).where(Hero.id == 1).values(age=31)

# DELETE
stmt = delete(Hero).where(Hero.id == 1)
```

这些 `stmt` 都是 Python 对象，最终由 SQLAlchemy 编译成对应数据库的 SQL。

## 4. ORM 完整示例

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Hero(Base):
    __tablename__ = "hero"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    secret_name: Mapped[str]
    age: Mapped[int | None]


engine = create_engine("sqlite:///./heroes_sa.db", echo=True)
Base.metadata.create_all(engine)

with Session(engine) as session:
    # 创建
    hero = Hero(name="Deadpond", secret_name="Dive Wilson", age=30)
    session.add(hero)
    session.commit()

    # 查询
    stmt = select(Hero).where(Hero.name == "Deadpond")
    result = session.execute(stmt)
    for h in result.scalars():
        print(h.id, h.name, h.age)
```

## 5. 事务

SQLAlchemy 默认开启事务，`commit()` 提交，`rollback()` 回滚。

```python
with Session(engine) as session:
    try:
        session.add(some_object)
        session.add(another_object)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

在 FastAPI 中，通常把 `Session` 作为依赖注入，请求结束后自动关闭；配合 `Session.begin()` 可以进一步简化事务。

## 6. 关系（Relationship）

关系是 ORM 的核心能力之一：

```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    heroes: Mapped[list["Hero"]] = relationship(back_populates="team")


class Hero(Base):
    __tablename__ = "hero"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))

    team: Mapped[Team | None] = relationship(back_populates="heroes")
```

常见关系加载策略：

| 策略 | 说明 | 适用场景 |
| --- | --- | --- |
| `select`（默认懒加载） | 首次访问关系时才查询 | 单对象读取 |
| `joined` | 主查询时 JOIN 关系表 | 列表页需要关系字段 |
| `selectin` | 用一条额外 IN 查询批量加载关系 | 列表页，避免 N+1 |

```python
from sqlalchemy.orm import selectinload

stmt = select(Hero).options(selectinload(Hero.team))
heroes = session.scalars(stmt).all()
```

## 7. SQLAlchemy 1.x vs 2.0

SQLAlchemy 2.0 是一次重要升级，主要变化：

- 推荐使用 `DeclarativeBase`、`Mapped`、`mapped_column`。
- `Session.execute()` 返回 `Result`，需要用 `.scalars()` 或 `.all()` 取对象。
- 统一了 Core 和 ORM 的查询接口：`select()` 同时适用于 Core 和 ORM。

SQLModel 基于 SQLAlchemy 2.0，因此学习 SQLAlchemy 2.0 风格即可。

## 8. SQLAlchemy 与 SQLModel 的关系

| 层级 | 对应物 |
| --- | --- |
| 数据库连接 | `create_engine` → SQLModel 复用 |
| 表元数据 | `MetaData` / `DeclarativeBase` → `SQLModel.metadata` |
| 字段定义 | `mapped_column()` → `Field(...)` |
| 模型类 | `DeclarativeBase` 子类 → `SQLModel` 子类 |
| 查询 | `select()` / `Session.execute()` → `session.exec()` |
| 关系 | `relationship()` → `Relationship()` |

SQLModel 并没有隐藏 SQLAlchemy，而是把它包成更简洁的 Pydantic 风格。当你遇到 SQLModel 解决不了的问题（复杂 join、CTE、原生 SQL、数据库特定特性），可以直接写 SQLAlchemy。

## 9. 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `Object not bound to a Session` | 对象所在 Session 已关闭 | 在 Session 上下文内使用对象，或主动 `session.refresh()` |
| 修改了对象但没写入数据库 | 只改了属性，没 `commit()` | 显式调用 `session.commit()` |
| 查询后拿不到对象 | 用了 `session.execute(stmt)` 没调 `.scalars()` | ORM 查询用 `.scalars().all()` |
| N+1 查询 | 懒加载关系，循环里多次触发 SQL | 用 `selectinload` 或 `joinedload` |
| 并发下 SQLite 报错 | SQLite 文件库默认锁粒度粗 | 加 `check_same_thread=False`，或减少并发写 |

## 10. 什么时候直接用 SQLAlchemy

虽然本章用 SQLModel，但以下场景建议直接写 SQLAlchemy：

- 已有大量 SQLAlchemy 1.x/2.0 代码，迁移成本过高。
- 需要复杂查询（CTE、窗口函数、复杂子查询）。
- 团队更熟悉 SQLAlchemy 原生 API。
- 需要精细控制数据库行为（事件监听、自定义类型）。

## 11. 总结

- SQLAlchemy 是 Python 数据库的“瑞士军刀”，ORM 和 Core 两种模式都很强大。
- Engine → Connection/Session → Table/Model → Expression 是它的核心链路。
- SQLModel 是 SQLAlchemy 的 Pydantic 风格封装，底层完全复用 SQLAlchemy。
- 学好 SQLAlchemy，能帮你更深入地理解 SQLModel、优化查询、排查数据库问题。

推荐练习：

1. 用纯 SQLAlchemy 2.0 重写本章的 Hero CRUD，体会 `mapped_column` 与 `Field` 的对应关系。
2. 给 Hero 增加 Team 关系，分别用懒加载、`joinedload`、`selectinload` 查询列表，对比 SQL 条数。
3. 用 Alembic 给表加一列 `created_at`，理解迁移文件和 `metadata` 的对应关系。
