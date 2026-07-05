# 02 路径参数与查询参数

掌握 URL 参数的两种传递方式及类型校验。

## 运行

```bash
cd tutorials/fastapi/02_path_query_params
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 路径参数 + 查询参数
curl "http://127.0.0.1:8000/items/3?q=phone"

# 多个路径参数
curl "http://127.0.0.1:8000/users/1/items/10?detail=true"

# 分页
curl "http://127.0.0.1:8000/items/?skip=0&limit=5"
```

## 知识点

- 路径参数：`/items/{item_id}`
- 查询参数：`?skip=0&limit=10`
- `Annotated[...]` 显式声明校验规则
- `Path()` 用于路径参数校验
- `Query()` 用于查询参数校验
- 类型注解错误时会自动返回 `422 Unprocessable Entity`
