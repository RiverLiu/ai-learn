# WebSocket 协议详解

HTTP 的典型模型是“一次请求，一次响应”。WebSocket 解决的是另一类问题：客户端和服务端需要在同一条连接上持续双向通信。

```text
HTTP:      Client -> Request  -> Server
           Client <- Response <- Server

WebSocket: Client <======== full-duplex connection ========> Server
```

WebSocket 常用于实时聊天、协作文档、实时看板、在线游戏、语音对话状态同步和模型生成过程中的双向控制。

## 本章文件

- [server.py](./server.py)：FastAPI WebSocket 服务端，包含 echo 和聊天室广播两个接口。
- [browser_client.html](./browser_client.html)：浏览器原生 WebSocket 客户端，不需要额外前端框架。

## 运行

在仓库根目录运行：

```bash
uv run uvicorn --app-dir tutorials/03_protocols/03_websockets server:app --reload
```

或者进入本目录运行：

```bash
cd tutorials/03_protocols/03_websockets
uv run uvicorn server:app --reload
```

打开浏览器：

```text
http://127.0.0.1:8000/client
```

打开两个浏览器标签页，分别点击“连接”，再发送消息，可以看到广播效果。

## WebSocket 握手

WebSocket 连接从 HTTP 开始。浏览器先发一个带升级头的 HTTP 请求：

```http
GET /ws/chat/demo-room?client_id=alice HTTP/1.1
Host: 127.0.0.1:8000
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
Sec-WebSocket-Version: 13
```

服务端同意升级后返回：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: ...
```

之后这条 TCP 连接不再按普通 HTTP 请求/响应交互，而是按 WebSocket frame 双向传输消息。

## 和 HTTP、SSE 的区别

| 协议 | 通信方向 | 连接生命周期 | 适合场景 |
| --- | --- | --- | --- |
| HTTP | 客户端请求，服务端响应 | 一次请求后结束 | REST API、普通 JSON 接口 |
| SSE | 服务端持续推送到客户端 | 长连接，单向 | LLM token 流、通知、进度事件 |
| WebSocket | 客户端和服务端双向通信 | 长连接，双向 | 聊天、协作、游戏、语音 Agent |

如果只是模型逐 token 输出，SSE 通常更简单。如果客户端也要频繁发控制消息，例如“暂停生成”“切换语音”“实时发送音频片段”，WebSocket 更合适。

## 服务端核心代码

Echo 接口最小结构：

```python
@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket, client_id: str = "anonymous"):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo",
                "client_id": client_id,
                "message": message,
            })
    except WebSocketDisconnect:
        print(f"echo client disconnected: {client_id}")
```

关键点：

- `await websocket.accept()`：接受握手，否则连接不会建立。
- `receive_text()`：等待客户端发消息。
- `send_json()`：向客户端发 JSON。
- `WebSocketDisconnect`：客户端断开时会抛出，必须清理连接状态。

## 广播模型

聊天室需要保存所有在线连接：

```text
client A -> server -> client A
                   -> client B
                   -> client C
```

本章用 `ConnectionManager` 维护：

```python
self.active_connections: dict[str, WebSocket] = {}
```

收到任意客户端消息后，服务端遍历所有连接并发送：

```python
await manager.broadcast({
    "type": "chat",
    "room_id": room_id,
    "client_id": client_id,
    "message": message,
})
```

真实业务里还要按 `room_id` 分组，不能把所有房间的消息都广播给所有人。本章为了突出协议概念，只保留最小结构。

## 浏览器客户端

浏览器原生支持 WebSocket：

```javascript
const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat/demo-room?client_id=alice");

socket.addEventListener("open", () => console.log("connected"));
socket.addEventListener("message", event => console.log(event.data));
socket.addEventListener("close", event => console.log(event.code));

socket.send("hello");
socket.close(1000, "user closed");
```

常见事件：

| 事件 | 含义 |
| --- | --- |
| `open` | 连接建立成功 |
| `message` | 收到服务端消息 |
| `error` | 连接或传输异常 |
| `close` | 连接关闭 |

## 消息格式

生产中不要只发裸字符串，建议统一 JSON envelope：

```json
{
  "type": "chat",
  "request_id": "req_001",
  "room_id": "demo-room",
  "client_id": "alice",
  "message": "你好",
  "timestamp": "2026-09-06T10:00:00Z"
}
```

`type` 很重要。它让客户端知道该如何处理消息：

- `chat`：普通聊天消息。
- `system`：系统通知。
- `error`：错误。
- `typing`：输入中。
- `tool_result`：工具调用结果。
- `audio_chunk`：音频片段。

## Ping / Pong 和心跳

WebSocket 是长连接。中间的代理、防火墙或负载均衡可能会关闭空闲连接。

常见处理：

- 客户端定时发 `ping` 消息。
- 服务端收到后回 `pong`。
- 如果连续多次没有响应，客户端主动重连。

示例消息：

```json
{"type": "ping"}
{"type": "pong"}
```

FastAPI/Starlette 底层和 ASGI 服务器也可能处理协议级 ping/pong，但应用层心跳仍然有价值，因为它能让业务知道“这个用户还在线”。

## 关闭连接和 Close Code

关闭连接时可以带 close code：

| Code | 含义 |
| --- | --- |
| `1000` | 正常关闭 |
| `1001` | 客户端离开页面或服务端重启 |
| `1008` | 策略违规，例如认证失败 |
| `1011` | 服务端内部错误 |

认证失败时，不要先建立连接再发普通错误消息。更好的做法是在握手或连接开始阶段验证 token，不合法就关闭连接。

## 认证和权限

WebSocket 不能像普通 HTTP 那样每次请求都重新带完整上下文。常见认证方式：

- Query 参数：`ws://host/ws?token=...`，简单但容易进入日志。
- Cookie：适合同域 Web 应用。
- 子协议或首条消息认证：连接后第一条消息发送 token。

教学项目可以用 `client_id` 模拟身份。生产项目必须验证真实 token，并在服务端保存连接对应的用户、租户、权限和房间。

## 重连和消息可靠性

WebSocket 连接可能随时断开。客户端应该实现重连：

```text
连接关闭
  ↓
等待 1s
  ↓
重连失败 -> 等待 2s
  ↓
重连失败 -> 等待 4s
```

如果消息不能丢，需要额外设计：

- `message_id`：每条消息唯一 ID。
- ack：客户端确认已收到。
- offset：重连后从某个位置继续拉取。
- 持久化：重要消息先写数据库，再广播。

WebSocket 本身不保证断线后的消息补偿。

## 背压和限流

如果服务端发得比客户端处理得快，会出现背压问题。生产中要考虑：

- 单连接发送队列长度。
- 单用户消息频率限制。
- 单房间最大连接数。
- 大消息大小限制。
- 慢客户端断开策略。

不要让一个慢连接拖慢整个广播循环。高并发场景通常会引入 Redis Pub/Sub、消息队列或专门的实时网关。

## 部署注意

部署 WebSocket 时，反向代理必须允许协议升级。

Nginx 常见配置：

```nginx
location /ws/ {
    proxy_pass http://app:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

还要注意：

- 使用 `wss://` 而不是明文 `ws://`。
- 负载均衡可能需要会话保持，或者把房间状态放到共享存储。
- 服务重启时要让客户端自动重连。
- 长连接会占用更多连接数和内存。

## 与 AI 应用的关系

WebSocket 在 AI 应用里常见于：

- 实时语音 Agent：客户端持续上传音频片段，服务端持续返回识别和回复。
- 多人协作助手：同一文档里多个用户共享 Agent 状态。
- 工具执行面板：服务端不断推送工具进度，客户端可以发送取消指令。
- 低延迟聊天：用户可以一边接收回复，一边发送中断或补充指令。

如果只是单向 token 流，优先考虑 SSE；如果需要双向控制，再考虑 WebSocket。

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 浏览器连接失败 | 服务端没有 `accept()` 或代理没升级协议 | 检查服务端和 Nginx Upgrade 头 |
| 本地能用，线上断开 | 代理空闲超时 | 配置心跳和代理 timeout |
| 消息串房间 | 广播没有按 room 分组 | 按 room_id 管理连接集合 |
| 用户越权收消息 | 连接没有绑定真实身份和权限 | 握手时校验 token 和房间权限 |
| 服务内存上涨 | 断开后没有清理连接 | 捕获 `WebSocketDisconnect` 并移除连接 |

## 练习

1. 给 `/ws/chat/{room_id}` 增加按房间隔离的连接管理。
2. 增加 `{"type": "ping"}` / `{"type": "pong"}` 应用层心跳。
3. 给消息添加 `message_id`，客户端重复发送时服务端去重。
4. 在连接时校验一个简单 token，例如 `?token=dev-token`。
5. 对比本章和 [08_fastapi/13_streaming_sse](../../08_fastapi/13_streaming_sse/)：什么时候选 SSE，什么时候选 WebSocket？
