# 网络协议基础

本目录介绍 Web 开发中常用的网络协议，重点讲解 HTTP/HTTPS 协议基础，以及如何用 Python 进行 HTTP 请求。
LLM API、Embedding API、MCP HTTP 传输、FastAPI 服务，本质上都跑在 HTTP 请求/响应模型之上。

## 目录

- `01_http_basics.md`：HTTP/HTTPS 协议基础
- `02_python_http/`：Python 中使用 HTTP 的示例代码

## 学习目标

1. 理解 HTTP 请求/响应模型
2. 掌握常见 HTTP 方法和状态码
3. 了解请求头、响应头的作用
4. 能够使用 Python 标准库和第三方库发送 HTTP 请求
5. 能看懂 LLM API 请求中的 URL、Header、JSON Body 和错误状态码

## 与 AI 应用的关系

| AI 应用概念 | HTTP 视角 |
| --- | --- |
| 调用 Chat Completions | `POST /v1/chat/completions` |
| 调用 Embeddings | `POST /v1/embeddings` |
| API Key | `Authorization` 请求头 |
| 流式输出 | HTTP 长连接 / SSE |
| FastAPI 后端 | 接收 HTTP 请求并返回 JSON 或流 |
| MCP Streamable HTTP | 基于 HTTP 的协议传输 |

学完本模块后，再看 [LLM API](../05_llm_api/) 和 [FastAPI](../08_fastapi/) 会更容易理解。
