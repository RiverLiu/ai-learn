# 01 Hello FastAPI

第一个 FastAPI 应用。

## 运行

```bash
cd tutorials/fastapi/01_hello_fastapi
uv run uvicorn main:app --reload
```

## 访问

- 首页：http://127.0.0.1:8000/
- 按 ID 获取项目：http://127.0.0.1:8000/items/42
- 交互式文档：http://127.0.0.1:8000/docs
- 替代文档：http://127.0.0.1:8000/redoc

## 核心概念

- `FastAPI()`：创建应用实例
- `@app.get("/")`：路径操作装饰器，将函数注册为 GET 接口
- 函数返回值会被自动序列化为 JSON
- 基于类型注解自动进行请求/响应校验并生成 OpenAPI 文档