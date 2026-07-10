# 07 数据库（SQLModel）

使用 SQLModel 完成数据库 CRUD。

## 运行

```bash
cd tutorials/fastapi/07_database_sqlmodel
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 创建英雄
curl -X POST "http://127.0.0.1:8000/heroes/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Deadpond","secret_name":"Dive Wilson","age":30}'

# 查询列表（默认 skip=0, limit=10）
curl "http://127.0.0.1:8000/heroes/"

# 分页查询：第 2 页，每页 5 条
curl "http://127.0.0.1:8000/heroes/?skip=5&limit=5"

# 更新
curl -X PUT "http://127.0.0.1:8000/heroes/1" \
  -H "Content-Type: application/json" \
  -d '{"name":"Deadpond","secret_name":"Dive Wilson","age":31}'

# 删除
curl -X DELETE "http://127.0.0.1:8000/heroes/1"
```

## 分页实现

本示例的列表接口已经实现了基于 `skip` / `limit` 的 offset 分页。

路由中定义查询参数：

```python
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(session: SessionDep, skip: int = 0, limit: int = 10):
    return get_heroes(session, skip=skip, limit=limit)
```

CRUD 中使用 SQLModel 的 `.offset()` 和 `.limit()`：

```python
def get_heroes(session: Session, skip: int = 0, limit: int = 10) -> list[Hero]:
    statement = select(Hero).offset(skip).limit(limit)
    return list(session.exec(statement).all())
```

如果需要返回总条数，可以封装统一的分页响应：

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    total: int
    items: list[T]
    skip: int
    limit: int
```

```python
@app.get("/heroes/", response_model=Page[HeroPublic])
def read_heroes(session: SessionDep, skip: int = 0, limit: int = 10):
    total = session.exec(select(func.count()).select_from(Hero)).one()
    heroes = get_heroes(session, skip=skip, limit=limit)
    return Page(total=total, items=heroes, skip=skip, limit=limit)
```

###  offset 分页的局限

- 数据量较小时简单直观，前端只需传 `skip` 和 `limit`。
- 当 `skip` 很大时（例如 `skip=100000`），数据库仍需扫描前面的所有行，性能会下降。
- 海量数据场景建议使用**游标分页**（cursor pagination），按唯一有序字段（如 `id`）过滤：

```python
@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    cursor: int | None = None,
    limit: int = 10,
):
    statement = select(Hero)
    if cursor:
        statement = statement.where(Hero.id > cursor)
    statement = statement.order_by(Hero.id).limit(limit)
    heroes = session.exec(statement).all()
    next_cursor = heroes[-1].id if heroes else None
    return {"items": heroes, "next_cursor": next_cursor}
```

## 知识点

- SQLModel = SQLAlchemy + Pydantic
- `create_engine` 创建数据库引擎
- `Session` 管理数据库会话
- `SessionDep` 作为依赖注入到路由中
- 模型分层：`Hero`（表模型）、`HeroCreate`（请求模型）、`HeroPublic`（响应模型）
- `@app.on_event("startup")` 在启动时建表
- 分页查询：`select(Hero).offset(skip).limit(limit)`
- offset 分页适合中小数据量，海量数据建议游标分页
