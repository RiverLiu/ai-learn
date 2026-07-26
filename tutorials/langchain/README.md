# LangChain 教程

LangChain 是最流行的 LLM 应用开发框架，把"调模型"封装成可组合的组件，
让提示词管理、输出解析、检索、工具调用等环节可以像搭积木一样组装。

## LangChain 生态三件套

| 项目 | 定位 | 类比 |
| --- | --- | --- |
| **LangChain** | 组件库 + LCEL 编排语言：模型、提示词、解析器、检索器 | 积木与说明书 |
| **LangGraph** | Agent 编排框架：状态图、循环、分支、持久化、人机协作 | 用积木搭机器人 |
| **LangSmith** | 观测与评估平台：调用链追踪（tracing）、数据集、效果评估 | 行车记录仪 + 考场 |

本教程讲 LangChain；[LangGraph 教程](../langgraph/)单独成章；LangSmith 在[第 6 章](./06_langsmith/)介绍。

## 章节目录

1. [01_chat_model](./01_chat_model/)：与聊天模型对话——消息、调用、流式输出
2. [02_prompts_parsers](./02_prompts_parsers/)：提示词模板与输出解析（含结构化输出）
3. [03_lcel](./03_lcel/)：LCEL——用 `|` 把组件组合成链
4. [04_rag](./04_rag/)：用 LangChain 重写 RAG 知识库问答
5. [05_tools](./05_tools/)：工具调用——让模型操作外部世界
6. [06_langsmith](./06_langsmith/)：LangSmith 追踪与评估

## 环境准备

依赖已包含在项目根目录的 `pyproject.toml` 中：

```bash
uv sync
```

本教程基于 **langchain 1.x**（2025 年 10 月发布的大版本，API 与旧版 0.x 差异较大，网上旧教程需注意）。

## 模型配置

代码默认走 OpenAI 兼容协议，通过环境变量（或项目根目录的 `.env` 文件）配置：

```bash
export OPENAI_API_KEY="sk-..."
# 使用兼容服务时追加（以 Kimi Code 为例，详见 tutorials/mcp/05_llm_agent/.env.example）：
export OPENAI_BASE_URL="https://api.kimi.com/coding/v1"
export MODEL_NAME="kimi-for-coding"
```

`ChatOpenAI` 会自动读取 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`，无需改代码。
注意：第 4 章还需要服务方提供 Embeddings 接口。

## 参考

- 官方文档：https://docs.langchain.com（新版）/ https://python.langchain.com
- LangGraph：https://langchain-ai.github.io/langgraph/
- LangSmith：https://smith.langchain.com
