# FastAPI 教程

FastAPI 是 Python 生态中构建 Web API 的主流框架。本模块从最小接口开始，逐步讲到请求参数、响应模型、
文件上传、依赖注入、数据库、JWT、CORS、WebSocket、测试、部署和 SSE 流式输出。

在 AI 应用里，FastAPI 常用于：

- 暴露 `/chat`、`/rag`、`/documents` 等后端接口。
- 处理文件上传和知识库管理。
- 用 SSE 或 WebSocket 向前端推送模型流式输出。
- 做鉴权、限流、任务状态查询和后台管理接口。

## 章节目录

1. [01_hello_fastapi](./01_hello_fastapi/)：第一个 FastAPI 应用，理解路由、启动和 Swagger UI
2. [02_path_query_params](./02_path_query_params/)：路径参数、查询参数和类型校验
3. [03_request_body](./03_request_body/)：请求体与 Pydantic 模型
4. [04_response_model](./04_response_model/)：响应模型、字段过滤和 API 输出契约
5. [05_form_files](./05_form_files/)：表单和文件上传，AI 知识库入口的基础
6. [06_dependencies](./06_dependencies/)：依赖注入，复用数据库连接、鉴权和配置
7. [07_database_sqlmodel](./07_database_sqlmodel/)：SQLModel 数据库基础和 CRUD
8. [08_auth_jwt](./08_auth_jwt/)：JWT 登录认证和受保护接口
9. [09_middleware_cors](./09_middleware_cors/)：中间件与 CORS，支持前端跨域访问
10. [10_websocket](./10_websocket/)：WebSocket 实时通信
11. [11_testing](./11_testing/)：FastAPI 测试、TestClient 和依赖覆盖
12. [12_deployment](./12_deployment/)：部署基础、环境变量和生产启动
13. [13_streaming_sse](./13_streaming_sse/)：SSE 流式输出，适合 LLM token streaming
14. [project_todo_api](./project_todo_api/)：完整 Todo API 项目，整合路由、认证、数据库和测试

## 快速开始

在仓库根目录执行：

```bash
cd tutorials/08_fastapi/01_hello_fastapi
uv run uvicorn main:app --reload
```

访问：

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## 学习路径

如果你只想为 AI 应用提供一个 HTTP 接口：

```text
01_hello_fastapi → 03_request_body → 04_response_model → 13_streaming_sse
```

如果你要做带登录、数据库和文件上传的完整后端：

```text
01_hello_fastapi → 05_form_files → 06_dependencies → 07_database_sqlmodel → 08_auth_jwt → 11_testing → 12_deployment
```

如果你要理解实时交互：

```text
10_websocket → 13_streaming_sse
```

## 与 AI 应用的关系

| AI 应用需求 | 对应章节 |
| --- | --- |
| Chat API | `01_hello_fastapi`、`03_request_body`、`04_response_model` |
| 文件上传到知识库 | `05_form_files` |
| 登录和多用户 | `08_auth_jwt` |
| RAG 文档和会话持久化 | `07_database_sqlmodel` |
| 前端跨域访问 | `09_middleware_cors` |
| 流式输出 token | `13_streaming_sse` |
| 实时双向通信 | `10_websocket` |
| 自动化测试 | `11_testing` |
| 上线部署 | `12_deployment` |

## 常见错误

**`uvicorn` 启动位置不对**

如果你在仓库根目录运行：

```bash
uv run uvicorn main:app --reload
```

通常会找不到 `main.py`。应先进入章节目录，或使用模块路径。

**浏览器打不开 `/docs`**

确认服务仍在运行，终端没有报错，端口是 `8000`。

**前端请求被 CORS 拦截**

看 [09_middleware_cors](./09_middleware_cors/)，后端需要显式允许前端来源。

## 练习建议

1. 跑通 `01_hello_fastapi`。
2. 用 `03_request_body` 写一个 `/chat` 请求体。
3. 用 `13_streaming_sse` 模拟 LLM 流式输出。
4. 用 `05_form_files` 上传一个 Markdown 文件。
5. 最后阅读 `project_todo_api`，理解一个完整 API 项目的组织方式。

## 常见面试题

**Q1：FastAPI 为什么适合 AI 应用后端？**

参考答案：它支持类型校验、自动文档、异步接口、依赖注入、文件上传和流式响应，适合构建 chat、RAG 和工具服务。

**Q2：Pydantic 在 FastAPI 中有什么作用？**

参考答案：Pydantic 用于请求/响应模型校验和序列化，能保证 API 输入输出契约稳定。

**Q3：SSE 和 WebSocket 如何选择？**

参考答案：SSE 适合服务端单向推送 token；WebSocket 适合双向实时交互和客户端频繁控制。普通聊天优先 SSE。

**Q4：依赖注入有什么价值？**

参考答案：依赖注入能复用数据库连接、鉴权、配置和服务对象，减少重复代码，也方便测试时替换依赖。

**Q5：CORS 是什么问题？**

参考答案：浏览器限制跨域请求。前端和后端域名不同时，后端必须显式允许来源、方法和请求头。

**Q6：为什么要定义 response_model？**

参考答案：它能约束响应结构、过滤不该返回的字段，并生成更准确的 OpenAPI 文档。

**Q7：文件上传在 AI 应用中常用于什么？**

参考答案：常用于知识库文档上传、图片理解、音频转写和数据分析任务入口。

**Q8：FastAPI 测试中 TestClient 的作用是什么？**

参考答案：TestClient 允许不启动真实服务器也能调用路由，适合测试请求校验、响应结构和依赖覆盖。

**Q9：生产启动和开发启动有什么区别？**

参考答案：开发常用 reload；生产应使用稳定进程管理、环境变量、日志、健康检查和反向代理。

**Q10：为什么 AI 接口要考虑超时？**

参考答案：模型、检索和工具调用可能耗时较长。超时能避免连接无限占用，并触发重试、降级或异步任务。
