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

## 常见面试题

**Q1：一次 HTTP 请求通常包含哪些部分？**

参考答案：通常包含请求方法、URL、请求头和请求体。调用 LLM API 时，方法多为 `POST`，请求头带认证信息，请求体通常是 JSON。

**Q2：HTTP 401、403、429、500 分别代表什么？**

参考答案：401 表示未认证或密钥无效；403 表示无权限；429 表示限流或额度不足；500 表示服务端错误。应用应分别做密钥检查、权限处理、退避重试和错误记录。

**Q3：GET 和 POST 的区别是什么？**

参考答案：GET 通常用于读取资源，参数常在 URL 中；POST 通常用于提交数据，请求体可包含 JSON。LLM API 通常用 POST，因为消息和参数需要放在请求体里。

**Q4：请求头 `Authorization` 的作用是什么？**

参考答案：它用于携带身份认证信息，例如 Bearer API Key。模型服务通过它判断调用者身份、权限和额度。

**Q5：什么是 JSON Body？**

参考答案：JSON Body 是 HTTP 请求体中的 JSON 数据。调用 Chat API 时，模型名、messages、temperature、tools 等字段都放在 JSON Body 中。

**Q6：HTTP 流式输出是怎么实现的？**

参考答案：服务端保持连接不关闭，逐步发送数据块。SSE 是常见方式，适合 LLM 按 token 或事件逐步返回结果。

**Q7：为什么要理解状态码？**

参考答案：状态码能帮助快速定位问题来源。比如 401 查密钥，404 查 URL 或接口路径，429 查限流，5xx 查服务端或重试策略。

**Q8：HTTPS 相比 HTTP 多了什么？**

参考答案：HTTPS 在 HTTP 之上加入 TLS 加密和证书校验，保护传输内容和身份可信。生产环境 API 调用必须使用 HTTPS，避免密钥和数据泄露。

**Q9：SSE 和普通 HTTP 响应有什么区别？**

参考答案：普通响应通常一次性返回完整数据，SSE 会持续推送事件。LLM 聊天中，SSE 能边生成边展示，降低用户感知延迟。

**Q10：OpenAI 兼容协议是什么意思？**

参考答案：不同服务商实现与 OpenAI API 类似的 URL、请求体和响应格式，使应用可以通过修改 `BASE_URL`、API Key 和模型名切换服务。
