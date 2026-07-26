# 06 MCP 协议细节

前几章用 SDK 把协议藏了起来。本章反其道而行：**不用任何 MCP 库**，手写 JSON 直接与
Server 对话——看完你会发现协议本体出人意料地小。

## 1. 地基：JSON-RPC 2.0

MCP 的所有消息都是 JSON-RPC 2.0 对象，只有三种：

| 消息 | 必备字段 | 说明 |
| --- | --- | --- |
| Request | `jsonrpc: "2.0"`、`id`、`method`（+`params`） | 带 `id` 的请求，对方**必须**回复 |
| Response | `jsonrpc: "2.0"`、同一个 `id`、`result` **或** `error` | 与请求用 `id` 配对 |
| Notification | `jsonrpc: "2.0"`、`method`（+`params`） | **无 `id`**，对方不回复 |

MCP 的方法名约定为 `类别/动作`，如 `tools/list`、`notifications/initialized`。

## 2. 生命周期：先握手，后通信

```
Client                                Server
  │── initialize ────────────────────▶│  提议 protocolVersion + 声明客户端能力
  │◀──────── result（版本+能力+信息）──  │  确认版本、声明服务端能力
  │── notifications/initialized ─────▶│  握手完成（此后才允许其他请求）
  │                                   │
  │── tools/list、tools/call ... ────▶│  正常通信阶段
  │                                   │
  │── （stdio：关闭 stdin；HTTP：DELETE 会话）──▶ 结束
```

- **协议版本协商**：客户端在 `initialize` 里提议自己支持的最新版本（如 `2025-06-18`），
  Server 若支持则原样确认；不支持则报错并附上自己支持的版本，客户端可降级重试。
- **能力（capabilities）声明**：双方各自声明自己支持的可选特性，之后通信中
  就**只允许**使用已声明的能力：
  - 客户端可声明：`roots`（提供可访问目录）、`sampling`（允许 Server 反向请求 LLM）、`elicitation`（允许 Server 向用户提问）
  - 服务端可声明：`tools` / `resources` / `prompts`，及各自的 `listChanged`（列表变化时推送通知）、`resources.subscribe`（订阅资源变更）

## 3. tools/call 的结果结构

```json
{
  "result": {
    "content": [{"type": "text", "text": "..."}],   // 内容块列表：text / image / audio / resource
    "structuredContent": {...},                      // 有 outputSchema 时的结构化数据
    "isError": false
  }
}
```

- `content` 是给模型/人看的内容块；`structuredContent` 是给程序用的结构化数据，
  二者可并存（对照第 2 章的 Pydantic 返回值）。
- 工具的参数约束在 `tools/list` 响应的 `inputSchema`、返回值约束在 `outputSchema`，
  都是标准 JSON Schema。

## 4. 错误的两层模型（本章脚本第 5、6、8 步的对比）

| 层 | 表现形式 | 例子 | 设计意图 |
| --- | --- | --- | --- |
| **工具级错误** | `result.isError: true`，错误文本放在 `content` 里 | 除数为 0、工具名不存在 | 错误作为**结果**回传，LLM 能读到原因并自我纠正 |
| **协议级错误** | 响应里是 `error` 而非 `result`：`{"code": ..., "message": ...}` | 未知方法、参数不符合协议 | 通信本身坏了，抛给客户端代码处理 |

协议级错误码沿用 JSON-RPC 标准：`-32700` 解析失败、`-32600` 无效请求、
`-32601` 方法不存在、`-32602` 参数无效、`-32603` 内部错误
（具体映射因 SDK 实现略有出入，以实测为准）。

## 5. 方法速查

| 方法 | 方向 | 作用 |
| --- | --- | --- |
| `initialize` / `ping` | C→S | 握手 / 探活 |
| `tools/list` / `tools/call` | C→S | 发现 / 调用工具 |
| `resources/list` / `resources/read` / `resources/templates/list` | C→S | 资源发现与读取 |
| `prompts/list` / `prompts/get` | C→S | 提示词模板 |
| `completion/complete` | C→S | 参数自动补全 |
| `logging/setLevel`、`notifications/message` | 双向 | 日志控制与服务端日志推送 |
| `notifications/cancelled` / `notifications/progress` | 双向 | 取消请求 / 进度汇报 |
| `sampling/createMessage` | **S→C** | Server 反向请求客户端跑 LLM |
| `roots/list` | **S→C** | Server 询问客户端可访问的根目录 |
| `elicitation/create` | **S→C** | Server 中途向用户索要结构化输入 |

注意后三个方向是 Server→Client——MCP 是**双向**协议，不止"客户端调服务端"。
列表类方法（`tools/list` 等）支持分页：响应带 `nextCursor`，
下次请求带 `params.cursor` 取下页。

## 6. 传输细节

- **stdio**：每条消息一行 JSON（`\n` 分隔）。推论：**Server 进程绝不能往 stdout
  print 任何业务输出**——那会直接污染协议流。这也是 FastMCP 把日志全走 stderr 的原因，
  你自己写 Server 时同样要遵守。
- **Streamable HTTP**：客户端 POST JSON 到单一端点；Server 可以直接回 JSON，
  也可以回 `text/event-stream`（SSE）推送多条消息；用 `Mcp-Session-Id` 头维护会话。

## 运行

```bash
uv run tutorials/mcp/06_protocol/main.py
```

脚本按生命周期顺序发 8 组消息并打印全部原始报文，重点对照：
第 4 步的 `structuredContent`、第 5/6 步的 `isError: true`、第 8 步的协议级 `error`。

## 核心概念

- **协议 = JSON-RPC 2.0 + 生命周期约定 + 一组方法名**，SDK 做的只是把这些
  变成趁手的函数。遇到 SDK 行为费解时，抓包看原始报文（或像本章一样手写一遍）
  是最快的理解方式。
- 完整规范：https://modelcontextprotocol.io/specification
