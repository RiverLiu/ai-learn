# 04 用 Python 编写 MCP Client

前几章都是用 Inspector 扮演 Client，本章自己动手：用 Python SDK 编写一个 MCP Client，
以 stdio 方式连接第 1 章的 `hello-mcp` Server，列出并调用其中的工具。

## 本章要点

- `StdioServerParameters`：描述如何启动 Server 子进程（命令 + 参数）。
- `stdio_client(...)`：启动子进程并建立 stdio 传输通道，返回读写流。
- `ClientSession`：MCP 会话对象，负责协议交互。
  - `initialize()`：握手，协商协议版本与双方能力。
  - `list_tools()` / `call_tool(name, args)`：发现工具、调用工具。
  - 同理还有 `list_resources()` / `read_resource(uri)`、`list_prompts()` / `get_prompt(...)`。

## 运行

在项目根目录执行（Client 会自行启动 Server 子进程，无需先手动启动 Server）：

```bash
uv run tutorials/mcp/04_mcp_client/client.py
```

预期输出：

```
可用工具：
  - add: 计算两个整数的和。
  - greet: 向指定的人问好。

add(19, 23) = 42
greet('小明') = 你好，小明！
```

## 核心概念

- **Client 即宿主**：任何嵌入了 MCP Client 的程序都能使用所有 MCP Server，这正是 MCP 的价值。
- **调用结果**：`call_tool` 返回的 `content` 是内容块列表（文本、图片等），
  若工具有结构化输出，还会有 `structuredContent` 字段。
