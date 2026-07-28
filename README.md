# AI 教程项目

本项目是一个面向 AI/编程学习的教程集合，使用 Python 进行示例演示。

## 当前内容

- `tutorials/tools/`：Python 开发工具（`venv` 虚拟环境、`uv` 包管理器、`uvicorn` ASGI 服务器）。
- `tutorials/protocols/`：HTTP/HTTPS 协议基础及 Python HTTP 客户端示例。
- `tutorials/fastapi/`：FastAPI 框架学习教程，从基础入门到完整项目实战。
- `tutorials/mcp/`：MCP（Model Context Protocol）教程，从编写 Server 到构建迷你 Agent。
- `tutorials/rag/`：RAG（检索增强生成）知识库教程，从 Embedding 到完整检索问答流水线。
- `tutorials/langchain/`：LangChain 1.x 教程，从模型调用、LCEL 到 RAG、工具调用与 LangSmith。
- `tutorials/langgraph/`：LangGraph 教程，从状态图、条件循环到 ReAct Agent、人机协作与会话持久化。
- `tutorials/memory/`：Agent 记忆教程，从短期记忆策略、长期记忆闭环到语义召回与 LangGraph Store。
- `tutorials/deepagents/`：Deep Agents 教程，基于 LangGraph 的深度代理——规划、上下文卸载、子代理、存储后端与人工审批。

## 环境要求

- Python >= 3.12
- 使用 [uv](https://docs.astral.sh/uv/) 管理依赖

## 安装依赖

```bash
uv sync
```

## 进入虚拟环境

```bash
source .venv/bin/activate
```

## FastAPI 教程快速开始

进入任意章节目录，例如：

```bash
cd tutorials/fastapi/01_hello_fastapi
uv run uvicorn main:app --reload
```

然后访问：

- 应用接口：http://127.0.0.1:8000
- 交互式 API 文档（Swagger UI）：http://127.0.0.1:8000/docs
- 替代文档（ReDoc）：http://127.0.0.1:8000/redoc

## License

本项目采用 [MIT License](LICENSE) 开源许可。
