# 11 测试

使用 TestClient 编写接口测试。

## 运行

```bash
cd tutorials/08_fastapi/11_testing
pytest -v
```

## 知识点

- `TestClient`：基于 `httpx` 的同步测试客户端
- `pytest` fixtures：复用测试资源
- `app.dependency_overrides`：覆盖依赖（如替换数据库、认证）
- 测试正常请求、异常请求、参数校验失败（422）
- 使用上下文管理器 `with TestClient(app)` 确保生命周期事件正确触发
