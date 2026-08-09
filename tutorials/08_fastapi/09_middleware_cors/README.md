# 09 中间件、CORS 与后台任务

学习请求生命周期、跨域和异步后台任务。

## 运行

```bash
cd tutorials/08_fastapi/09_middleware_cors
uv run uvicorn main:app --reload
```

## 测试接口

```bash
# 查看响应头中的 X-Process-Time
curl -v "http://127.0.0.1:8000/"

# 触发后台任务
curl -X POST "http://127.0.0.1:8000/send-notification/alice@example.com"

# 查看后台写入的日志
cat log.txt
```

## 知识点

- `@app.middleware("http")` 自定义中间件
- `CORSMiddleware` 解决跨域问题
- `BackgroundTasks` 执行不阻塞响应的后台任务
- `lifespan` 管理应用启动和关闭事件
- 中间件按添加顺序执行
