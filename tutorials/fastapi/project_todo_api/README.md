# 综合项目：Todo API

一个完整的待办事项 RESTful API，整合了 FastAPI 前面章节的核心知识。

## 功能

- 用户注册 / 登录
- JWT Token 认证
- 待办事项增删改查
- 用户只能看到自己的待办事项
- 完整测试覆盖

## 技术栈

- FastAPI
- SQLModel + SQLite
- JWT（python-jose + passlib）
- pytest + TestClient

## 运行

```bash
cd tutorials/fastapi/project_todo_api
uv run uvicorn app.main:app --reload
```

## 测试

```bash
pytest -v
```

## API 列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/token` | 登录获取 JWT |
| POST | `/users/` | 用户注册 |
| GET  | `/users/me` | 获取当前用户信息 |
| POST | `/todos/` | 创建待办 |
| GET  | `/todos/` | 查询待办列表 |
| GET  | `/todos/{id}` | 查询单个待办 |
| PUT  | `/todos/{id}` | 更新待办 |
| DELETE | `/todos/{id}` | 删除待办 |

## 快速体验

```bash
# 1. 注册
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret"}'

# 2. 登录获取 token
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/token" \
  -d "username=alice&password=secret" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. 创建待办
curl -X POST "http://127.0.0.1:8000/todos/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"学习 FastAPI","description":"完成所有章节"}'

# 4. 查询待办列表
curl "http://127.0.0.1:8000/todos/" \
  -H "Authorization: Bearer $TOKEN"
```
