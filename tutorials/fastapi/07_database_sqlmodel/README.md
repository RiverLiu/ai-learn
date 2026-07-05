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

# 查询列表
curl "http://127.0.0.1:8000/heroes/"

# 更新
curl -X PUT "http://127.0.0.1:8000/heroes/1" \
  -H "Content-Type: application/json" \
  -d '{"name":"Deadpond","secret_name":"Dive Wilson","age":31}'

# 删除
curl -X DELETE "http://127.0.0.1:8000/heroes/1"
```

## 知识点

- SQLModel = SQLAlchemy + Pydantic
- `create_engine` 创建数据库引擎
- `Session` 管理数据库会话
- `SessionDep` 作为依赖注入到路由中
- 模型分层：`Hero`（表模型）、`HeroCreate`（请求模型）、`HeroPublic`（响应模型）
- `@app.on_event("startup")` 在启动时建表
