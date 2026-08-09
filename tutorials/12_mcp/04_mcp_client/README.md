# 04 用 Python 编写 MCP Client

前几章都是用 Inspector 扮演 Client，本章自己动手：用 Python SDK 编写 MCP Client，
分别通过 **stdio**（`client.py`）和 **SSE / Streamable HTTP**（`client_http.py`）
三种传输连接 Server，列出并调用其中的工具。

## 本章要点

- `StdioServerParameters`：描述如何启动 Server 子进程（命令 + 参数）。
- `stdio_client(...)`：启动子进程并建立 stdio 传输通道，返回读写流。
- `ClientSession`：MCP 会话对象，负责协议交互。
  - `initialize()`：握手，协商协议版本与双方能力。
  - `list_tools()` / `call_tool(name, args)`：发现工具、调用工具。
  - 同理还有 `list_resources()` / `read_resource(uri)`、`list_prompts()` / `get_prompt(...)`。

## 三种传输对比

| 传输 | Server 形态 | Client 建立通道 | 适用场景 |
| --- | --- | --- | --- |
| stdio | Client 启动的本地子进程 | `stdio_client(server_params)` | 本地工具，最常见 |
| Streamable HTTP | 独立 HTTP 服务（`/mcp` 端点） | `streamable_http_client(url)` | 远程/多用户，现行标准 |
| SSE（旧版） | 独立 HTTP 服务（`/sse` 端点） | `sse_client(url)` | 已被 Streamable HTTP 取代，仅兼容旧服务 |

**只有建立通道这一步不同**；拿到读写流之后，`ClientSession` 的用法完全一致——
协议报文与传输解耦（报文细节见[第 6 章](../06_protocol/)）。

## 运行

方式一：stdio（Client 会自行启动 Server 子进程，无需先手动启动 Server）：

```bash
uv run tutorials/12_mcp/04_mcp_client/client.py
```

方式二：Streamable HTTP（先启 Server，再开另一个终端跑 Client）：

```bash
uv run tutorials/12_mcp/04_mcp_client/server_http.py            # 终端 1：监听 127.0.0.1:8000/mcp
uv run tutorials/12_mcp/04_mcp_client/client_http.py http       # 终端 2
```

方式三：旧版 SSE：

```bash
uv run tutorials/12_mcp/04_mcp_client/server_http.py sse        # 终端 1：监听 127.0.0.1:8000/sse
uv run tutorials/12_mcp/04_mcp_client/client_http.py sse        # 终端 2
```

三种方式的预期输出一致：

```
可用工具：
  - add: 计算两个整数的和。
  - greet: 向指定的人问好。

add(19, 23) = 42
greet('小明') = 你好，小明！
```

## 核心概念

- **Client 即宿主**：任何嵌入了 MCP Client 的程序都能使用所有 MCP Server，这正是 MCP 的价值。
- **传输可换、协议不变**：同一个 Server 把 `mcp.run()` 的 transport 参数一改就能从
  子进程变成网络服务；客户端只换建立通道的那一行。
- **调用结果**：`call_tool` 返回的 `content` 是内容块列表（文本、图片等），
  若工具有结构化输出，还会有 `structuredContent` 字段。
