# 13 SSE 流式输出

AI 应用的标配体验：回答逐段"打"出来，而不是转圈等一整段。
这一章用 FastAPI `StreamingResponse` + OpenAI 流式接口实现。

## SSE vs WebSocket（第 10 章）

| | SSE | WebSocket |
| --- | --- | --- |
| 方向 | 服务器 → 浏览器**单向** | 双向 |
| 协议 | 普通 HTTP | 独立的 ws 协议 |
| 断线重连 | 浏览器自动 | 要自己实现 |
| 浏览器 API | `EventSource` | `WebSocket` |
| 适用 | 流式回答、进度推送 | 实时协作、聊天室 |

**AI 流式回答选 SSE 就够了**——用户发完一句话后，数据只从服务器流向浏览器。

## 本章要点

- SSE 消息格式极简：`data: 内容\n\n`（`data: ` 开头、两个换行结尾）。
- `StreamingResponse(生成器, media_type="text/event-stream")`：FastAPI 把生成器的
  每次 `yield` 即时推给客户端。
- **同步生成器 vs 异步生成器**：本章用同步 `openai` 客户端 + 同步生成器，
  StreamingResponse 会放到线程池执行，不阻塞事件循环；若在 `async` 生成器里
  直接调同步 SDK，会把整个事件循环卡死（新手高频坑）。
- 经反向代理部署时加 `X-Accel-Buffering: no`，否则 nginx 会攒缓冲，流式变批量。

## 运行

```bash
cd tutorials/08_fastapi/13_streaming_sse
uv run uvicorn main:app --reload
```

方式一：命令行看流式（`-N` 关闭 curl 缓冲；中文参数要用 `--data-urlencode` 编码，否则报 400）：

```bash
curl -N -G "http://127.0.0.1:8000/chat" --data-urlencode "message=讲个笑话"
```

方式二：浏览器打开 http://127.0.0.1:8000 ，输入问题点发送，看打字机效果。

## 核心概念

- `stream=True`：OpenAI 接口的流式开关，返回的每个 chunk 只含增量文本
  （`choices[0].delta.content`），拼起来才是完整回答。
- SSE 单条消息里不能有真实换行（格式以换行分隔），代码里把 `\n` 转义，前端再转回来。
- 生产环境可在流里夹杂自定义事件（`event: status` / `data: ...`），
  用来先推"正在检索"再推正文——[capstone 项目](../../20_capstone/)有完整示范。
