# 03 请求体

使用 Pydantic 模型定义和校验请求体。

## 运行

```bash
cd tutorials/fastapi/03_request_body
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 创建商品
curl -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Phone", "price": 5999.0, "tax": 0.1}'

# 更新商品
curl -X PUT "http://127.0.0.1:8000/items/3?q=update" \
  -H "Content-Type: application/json" \
  -d '{"name": "Phone", "price": 5999.0}'

# 嵌套模型
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tom", "age": 30, "address": {"city": "Beijing", "country": "China"}}'
```

## 知识点

- `BaseModel`：定义请求体结构
- `Field()`：字段校验与默认值
- 嵌套模型：模型字段可以是另一个模型
- 路径参数、请求体、查询参数可同时使用
- 校验失败会返回详细的 422 错误信息
