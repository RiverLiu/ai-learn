# AI 开发教程

面向**大学生与在职工程师**的 AI 应用开发系统教程，使用 Python，全部示例可运行。
主线目标：从零基础到能独立构建生产级 LLM 应用（RAG、Agent、MCP、评估与部署）。

## 学习路线图

难度：⭐ 入门　⭐⭐ 基础　⭐⭐⭐ 进阶

| 顺序 | 模块 | 内容 | 难度 |
| --- | --- | --- | --- |
| 1 | [tutorials/tools](tutorials/tools/) | 开发工具：venv、uv 包管理、uvicorn | ⭐ |
| 2 | [tutorials/basic](tutorials/basic/) | Python 基础：json、asyncio、aiohttp | ⭐ |
| 3 | [tutorials/protocols](tutorials/protocols/) | HTTP/HTTPS 协议与 Python HTTP 客户端 | ⭐⭐ |
| 4 | [tutorials/llm_api](tutorials/llm_api/) | **第一次调用 LLM API**：消息、参数、流式、工具调用、错误处理 | ⭐ |
| 5 | [tutorials/prompt](tutorials/prompt/) | **提示词工程**：结构、few-shot、输出控制、思维链、迭代方法 | ⭐⭐ |
| 6 | [tutorials/rag](tutorials/rag/) | RAG：Embedding、切块、向量库、检索问答 | ⭐⭐ |
| 7 | [tutorials/fastapi](tutorials/fastapi/) | FastAPI 框架：12 章 + Todo API 完整项目 | ⭐⭐ |
| 8 | [tutorials/langchain](tutorials/langchain/) | LangChain 1.x：组件、LCEL、RAG、工具、LangSmith | ⭐⭐⭐ |
| 9 | [tutorials/langgraph](tutorials/langgraph/) | LangGraph：状态图、循环、ReAct Agent、人机协作、持久化 | ⭐⭐⭐ |
| 10 | [tutorials/memory](tutorials/memory/) | Agent 记忆：短期策略、长期闭环、语义召回、Store | ⭐⭐⭐ |
| 11 | [tutorials/mcp](tutorials/mcp/) | MCP：Server/Client、三种原语、协议细节 | ⭐⭐⭐ |
| 12 | [tutorials/skills](tutorials/skills/) | Skills：把可复用经验封装成 Agent 能自动加载的能力包 | ⭐⭐⭐ |
| 13 | [tutorials/deepagents](tutorials/deepagents/) | Deep Agents：规划、上下文卸载、子代理、存储后端 | ⭐⭐⭐ |
| 14 | [tutorials/evaluation](tutorials/evaluation/) | 评估：评估集、LLM-as-judge、RAG 检索指标 | ⭐⭐⭐ |
| 15 | [tutorials/local_models](tutorials/local_models/) | 本地模型：Ollama、本地 Embedding（离线/合规场景） | ⭐⭐ |
| 16 | [tutorials/security](tutorials/security/) | LLM 应用安全：提示词注入、间接注入、纵深防御 | ⭐⭐⭐ |
| 17 | [tutorials/multimodal](tutorials/multimodal/) | 多模态：图像理解、语音转写（ASR→LLM 管道） | ⭐⭐ |
| 18 | [tutorials/multi_agent](tutorials/multi_agent/) | 多 Agent 设计模式：流水线、主管、交接 | ⭐⭐⭐ |
| 19 | [tutorials/capstone](tutorials/capstone/) | **毕业项目**：云雀笔记智能客服（RAG+Agent+SSE 流式+评测） | ⭐⭐⭐ |

## 分角色学习路径

- **零基础大学生（建议 14-16 周）**：按路线图顺序学习，每周 1 个模块。
  tools/basic 跟不上时先补 Python 语法。
- **在职工程师（建议 4 周速成）**：已会 Python 和 Web 开发，可直接从第 4 站开始：
  `llm_api → prompt → rag → langchain → langgraph → memory → mcp → skills → deepagents`，
  tools/protocols/fastapi 按需查阅，evaluation 与 local_models 收尾。

## 章节结构约定

每章包含 `README.md` + 可运行代码，统一章节结构：本章要点 → 运行 → 核心概念 →
常见错误 → 练习建议。运行方式均为在仓库根目录执行 `uv run <章节脚本>`。

## 环境要求

- Python >= 3.12
- 使用 [uv](https://docs.astral.sh/uv/) 管理依赖

## 安装依赖

```bash
uv sync
```

## 模型配置（统一约定）

凡涉及 LLM 调用的章节，统一读取**项目根目录的 `.env`**（各章代码 `load_dotenv()` 向上查找）：

```bash
# .env（已被 .gitignore 忽略）
OPENAI_API_KEY=sk-...
# 使用 OpenAI 兼容服务时（注意：BASE_URL 只到 /v1 为止，不要带接口路径后缀）：
OPENAI_BASE_URL=https://api.kimi.com/coding/v1
MODEL_NAME=kimi-for-coding
EMBEDDING_MODEL=text-embedding-3-small   # 仅 RAG/评估等需要向量模型的章节
```

本地/离线方案见 [tutorials/local_models](tutorials/local_models/)。
常见配置错误见 [踩坑 FAQ](tutorials/faq.md)，生词见 [术语表](tutorials/glossary.md)。

## FastAPI 教程快速开始

```bash
cd tutorials/fastapi/01_hello_fastapi
uv run uvicorn main:app --reload
```

然后访问：http://127.0.0.1:8000 与 http://127.0.0.1:8000/docs

## License

本项目采用 [MIT License](LICENSE) 开源许可。
