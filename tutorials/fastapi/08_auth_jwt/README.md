# 08 认证与授权（JWT）

实现基于 JWT 的用户登录和受保护路由。

## 运行

```bash
cd tutorials/fastapi/08_auth_jwt
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 1. 登录获取 token（用户名 alice，密码 secret）
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/token" \
  -d "username=alice&password=secret" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. 访问受保护接口
curl "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"

# 或在 /docs 中点击右上角 Authorize 按钮，输入用户名密码测试
```

## 知识点

- OAuth2 Password Bearer：`OAuth2PasswordBearer(tokenUrl="token")`
- JWT 生成与验证：`python-jose` + `passlib`
- 密码哈希存储
- `Depends(get_current_active_user)` 保护路由
- 401 未授权响应

## 注意

示例中 `SECRET_KEY` 硬编码在代码里，生产环境务必使用环境变量。
