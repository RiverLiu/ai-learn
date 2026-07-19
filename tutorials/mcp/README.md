# MCP（Model Context Protocol）教程

MCP 是 Anthropic 于 2024 年底发布的开放协议，用于标准化 **LLM 应用与外部数据源、工具之间的连接**。
可以把它类比为 AI 应用领域的 "USB-C 接口"：工具/数据源只要实现一次 MCP Server，
就能被任何支持 MCP 的客户端（Claude Desktop、Kimi CLI、ChatGPT 等）直接使用。

## 为什么需要 MCP

没有 MCP 时，让 LLM 调用外部能力需要为每个模型、每个工具单独写适配代码（N 个模型 × M 个工具 = N×M 种集成）。
MCP 把这件事变成两套标准接口：工具方实现 MCP Server，应用方实现 MCP Client，集成成本降为 N+M。

## 核心架构

```
┌─────────────────────────────────────┐
│  App（宿主应用，如 Claude Desktop） │
│  ┌──────────┐      ┌──────────┐     │
│  │ Client 1 │      │ Client 2 │     │
│  └────┬─────┘      └────┬─────┘     │
└───────┼─────────────────┼───────────┘
        │ MCP 协议        │ MCP 协议
   ┌────┴─────┐      ┌────┴─────┐
   │ Server A │      │ Server B │   ← 各自连接本地文件、数据库、Web API 等
   └──────────┘      └──────────┘
```

- **App**：用户直接使用的 AI 应用，内部为每个 Server 维护一个 Client。
- **Client**：与某个 Server 保持一对一连接，负责协议协商与消息转发。
- **Server**：轻量程序，通过三种**原语（primitives）**对外暴露能力：

| 原语 | 作用 | 由谁触发 |
| --- | --- | --- |
| **Tools** | 可执行的函数（查天气、发消息、操作数据库） | 模型（需用户批准） |
| **Resources** | 可读取的数据（文件内容、配置、记录） | 应用/用户 |
| **Prompts** | 预定义的提示词模板 | 用户 |

## 传输方式（Transports）

- **stdio**：Client 把 Server 作为本地子进程启动，通过标准输入输出通信。适合本地工具，最常见。
- **Streamable HTTP**：Server 作为独立 HTTP 服务运行，适合远程/多用户场景（旧版 SSE 传输已被其取代）。

## 章节目录

1. [01_hello_mcp](./01_hello_mcp/)：第一个 MCP Server（FastMCP 快速上手 + Inspector 调试）
2. [02_tools](./02_tools/)：工具进阶（类型注解、异步、错误处理、结构化输出）
3. [03_resources_prompts](./03_resources_prompts/)：Resources 与 Prompts
4. [04_mcp_client](./04_mcp_client/)：用 Python 编写 MCP Client
5. [05_llm_agent](./05_llm_agent/)：结合 OpenAI function calling 构建迷你 Agent

## 环境准备

依赖已包含在项目根目录的 `pyproject.toml` 中（`mcp[cli]`），直接执行：

```bash
uv sync
```

第 1 章的可视化调试工具 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 还需要 Node.js（通过 `npx` 运行）。

## 参考

- 官方文档：https://modelcontextprotocol.io
- Python SDK：https://github.com/modelcontextprotocol/python-sdk
