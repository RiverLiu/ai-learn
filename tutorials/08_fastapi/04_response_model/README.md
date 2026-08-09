# 04 响应模型与状态码

控制接口返回的数据结构和 HTTP 状态码。

## 运行

```bash
cd tutorials/08_fastapi/04_response_model
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 创建用户：输入包含密码，输出自动隐藏
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret","email":"alice@example.com","full_name":"Alice"}'

# 查询存在的用户
curl "http://127.0.0.1:8000/users/1"

# 查询不存在的用户，返回 404
curl "http://127.0.0.1:8000/users/99"

# 创建商品：未设置的 tax 字段不会出现在响应中
curl -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Book","price":29.9}'
```

## 知识点

- `response_model`：过滤/序列化输出数据
- `status_code`：设置默认 HTTP 状态码
- `response_model_exclude_unset=True`：只返回已设置字段
- `HTTPException`：抛出带状态码和详情的异常
- 利用不同模型实现输入输出字段差异（如隐藏密码）
