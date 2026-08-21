# AI 开发教程

面向**大学生与在职工程师**的 AI 应用开发系统教程，使用 Python，基础示例可运行，高级专题面向生产工程化。
主线目标：从零基础到能独立构建生产级 LLM 应用（RAG、Agent、MCP、评估、观测与部署）。

本项目分为两层：

- [tutorials](tutorials/)：基础教程，讲清 LLM 应用开发的核心概念和最小可运行实现。
- [advanced](advanced/)：高级教程，讲生产级 AI 应用的架构、数据管道、测试、可观测性、成本优化、前端交互、后台任务和部署。

## 基础学习路线图

难度：⭐ 入门　⭐⭐ 基础　⭐⭐⭐ 进阶

| 顺序 | 模块 | 内容 | 难度 |
| --- | --- | --- | --- |
| 1 | [tutorials/01_tools](tutorials/01_tools/) | 开发工具：venv、uv 包管理、uvicorn | ⭐ |
| 2 | [tutorials/02_basic](tutorials/02_basic/) | Python 基础：json、asyncio、aiohttp | ⭐ |
| 3 | [tutorials/03_protocols](tutorials/03_protocols/) | HTTP/HTTPS 协议与 Python HTTP 客户端 | ⭐⭐ |
| 4 | [tutorials/04_transformer](tutorials/04_transformer/) | Transformer 原理：Token、Embedding、Attention、Decoder 生成 | ⭐⭐ |
| 5 | [tutorials/05_llm_api](tutorials/05_llm_api/) | **第一次调用 LLM API**：消息、参数、流式、工具调用、错误处理 | ⭐ |
| 6 | [tutorials/06_prompt](tutorials/06_prompt/) | **提示词工程**：结构、few-shot、输出控制、思维链、迭代方法 | ⭐⭐ |
| 7 | [tutorials/07_rag](tutorials/07_rag/) | RAG：Embedding、切块、向量库、检索问答 | ⭐⭐ |
| 8 | [tutorials/08_fastapi](tutorials/08_fastapi/) | FastAPI 框架：12 章 + Todo API 完整项目 | ⭐⭐ |
| 9 | [tutorials/09_langchain](tutorials/09_langchain/) | LangChain 1.x：组件、LCEL、RAG、工具、LangSmith | ⭐⭐⭐ |
| 10 | [tutorials/10_langgraph](tutorials/10_langgraph/) | LangGraph：状态图、循环、ReAct Agent、人机协作、持久化 | ⭐⭐⭐ |
| 11 | [tutorials/11_memory](tutorials/11_memory/) | Agent 记忆：短期策略、长期闭环、语义召回、Store | ⭐⭐⭐ |
| 12 | [tutorials/12_mcp](tutorials/12_mcp/) | MCP：Server/Client、三种原语、协议细节 | ⭐⭐⭐ |
| 13 | [tutorials/13_skills](tutorials/13_skills/) | Skills：把可复用经验封装成 Agent 能自动加载的能力包 | ⭐⭐⭐ |
| 14 | [tutorials/14_deepagents](tutorials/14_deepagents/) | Deep Agents：规划、上下文卸载、子代理、存储后端 | ⭐⭐⭐ |
| 15 | [tutorials/15_evaluation](tutorials/15_evaluation/) | 评估：评估集、LLM-as-judge、RAG 检索指标 | ⭐⭐⭐ |
| 16 | [tutorials/16_local_models](tutorials/16_local_models/) | 本地模型：Ollama、本地 Embedding（离线/合规场景） | ⭐⭐ |
| 17 | [tutorials/17_security](tutorials/17_security/) | LLM 应用安全：提示词注入、间接注入、纵深防御 | ⭐⭐⭐ |
| 18 | [tutorials/18_multimodal](tutorials/18_multimodal/) | 多模态：图像理解、语音转写（ASR→LLM 管道） | ⭐⭐ |
| 19 | [tutorials/19_multi_agent](tutorials/19_multi_agent/) | 多 Agent 设计模式：流水线、主管、交接 | ⭐⭐⭐ |
| 20 | [tutorials/20_capstone](tutorials/20_capstone/) | **毕业项目**：云雀笔记智能客服（RAG+Agent+SSE 流式+评测） | ⭐⭐⭐ |
| 21 | [tutorials/21_planning](tutorials/21_planning/) | Agent Planning：计划、分层规划、动态重规划 | ⭐⭐⭐ |

## 高级学习路线图

高级教程默认读者已经完成基础路线中的 `05_llm_api → 06_prompt → 07_rag → 08_fastapi → 09_langchain/10_langgraph → 15_evaluation → 20_capstone`。

| 顺序 | 模块 | 内容 | 目标 |
| --- | --- | --- | --- |
| 1 | [advanced/01_product_architecture](advanced/01_product_architecture/) | 产品架构、模块边界、数据流 | 从 demo 设计走向工程架构 |
| 2 | [advanced/02_knowledge_engineering](advanced/02_knowledge_engineering/) | 文档摄取、元数据、增量索引 | 建立可治理知识库 |
| 3 | [advanced/03_production_rag](advanced/03_production_rag/) | hybrid search、rerank、query rewrite、失败分析 | 提升 RAG 质量 |
| 4 | [advanced/04_agent_engineering](advanced/04_agent_engineering/) | 工具权限、Agent 轨迹、Skills 生产化、人工审批 | 让 Agent 可控 |
| 5 | [advanced/05_quality_engineering](advanced/05_quality_engineering/) | LLM 测试、评估 CI、Prompt 回归 | 建立质量防线 |
| 6 | [advanced/06_observability_cost](advanced/06_observability_cost/) | trace、反馈闭环、token 成本、延迟优化 | 能定位问题并控制成本 |
| 7 | [advanced/07_user_experience](advanced/07_user_experience/) | Chat UI、SSE、文件上传、引用展示 | 做出可用产品界面 |
| 8 | [advanced/08_async_workflows](advanced/08_async_workflows/) | 队列、批量 embedding、长任务状态、取消和重试 | 支撑长任务 |
| 9 | [advanced/09_deployment_operations](advanced/09_deployment_operations/) | Docker Compose、Nginx、数据库、向量库、灰度回滚 | 完成生产部署 |
| 10 | [advanced/10_production_capstone](advanced/10_production_capstone/) | 将毕业项目升级成生产级 AI 应用 | 综合实战 |

## 分角色学习路径

- **零基础大学生（建议 14-16 周）**：按路线图顺序学习，每周 1 个模块。
  `01_tools` / `02_basic` 跟不上时先补 Python 语法。
- **在职工程师（建议 4 周速成）**：已会 Python 和 Web 开发，可直接从第 5 站开始：
  `05_llm_api → 06_prompt → 07_rag → 09_langchain → 10_langgraph → 11_memory → 12_mcp → 13_skills → 14_deepagents`，
  `01_tools` / `03_protocols` / `08_fastapi` 按需查阅，`15_evaluation` 与 `16_local_models` 收尾。
- **准备做生产项目的工程师（建议 3-6 周）**：先跑通 `tutorials/20_capstone`，
  再学习 `advanced/01_product_architecture → advanced/02_knowledge_engineering → advanced/03_production_rag →
  advanced/05_quality_engineering → advanced/06_observability_cost → advanced/09_deployment_operations`。

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

本地/离线方案见 [tutorials/16_local_models](tutorials/16_local_models/)。
常见配置错误见 [踩坑 FAQ](tutorials/faq.md)，生词见 [术语表](tutorials/glossary.md)。

## FastAPI 教程快速开始

```bash
cd tutorials/08_fastapi/01_hello_fastapi
uv run uvicorn main:app --reload
```

然后访问：http://127.0.0.1:8000 与 http://127.0.0.1:8000/docs

## License

本项目采用 [MIT License](LICENSE) 开源许可。
