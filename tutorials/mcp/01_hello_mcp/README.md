# 01 Hello MCP

第一个 MCP Server：用官方 Python SDK 提供的 **FastMCP** 暴露两个工具（`add`、`greet`）。

## 关键点

- `FastMCP("hello-mcp")`：创建 Server 实例。
- `@mcp.tool()`：把一个普通 Python 函数注册为 MCP 工具。
  **类型注解和 docstring 是必需的**——SDK 会根据它们生成工具的 JSON Schema 和描述，LLM 靠这些信息决定何时、如何调用工具。
- `mcp.run()`：默认使用 stdio 传输。stdio Server **不是** HTTP 服务，不能用浏览器或 curl 访问，
  它由 MCP Client 以子进程方式启动，通过标准输入输出通信。

## 运行

方式一：用 MCP Inspector 可视化调试（推荐，需要 Node.js）：

```bash
cd tutorials/mcp/01_hello_mcp
uv run mcp dev server.py
```

浏览器打开终端中提示的地址（默认 http://127.0.0.1:6274），在 **Tools** 标签页即可看到并调用 `add`、`greet`。

方式二：直接以 stdio 方式启动（通常由 Client 代为启动，手动运行会挂起等待输入）：

```bash
uv run python server.py
```

方式三：在宿主应用中配置使用。以 Kimi CLI / Claude Desktop 风格的配置为例：

```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "uv",
      "args": ["run", "python", "tutorials/mcp/01_hello_mcp/server.py"]
    }
  }
}
```

## 核心概念

- **Tool**：Server 暴露给 LLM 的可执行函数。
- **stdio 传输**：Client 启动 Server 子进程，双方通过 stdin/stdout 交换 JSON-RPC 消息。
- **MCP Inspector**：官方调试工具，扮演 Client 角色，可以在不写任何客户端代码的情况下测试 Server。
