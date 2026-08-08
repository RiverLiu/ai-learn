# 基础教程

`tutorials/` 是本项目的基础教程区，目标是让学习者从 Python 与 HTTP 开始，逐步掌握构建 LLM 应用所需的核心能力：

- 会调用模型 API，理解消息、参数、流式输出、工具调用和错误处理。
- 会理解 Transformer 的基本原理：token、embedding、attention 和自回归生成。
- 会写 Prompt，并能用评估集迭代 Prompt。
- 会构建最小 RAG：embedding、切块、向量检索、引用回答。
- 会用 FastAPI 暴露 AI 应用接口。
- 会使用 LangChain、LangGraph、MCP、Skills、Deep Agents 等上层框架。
- 会理解记忆、多 Agent、安全、多模态和本地模型的基础设计。

基础教程强调“先跑通、再理解、最后组合”。每章尽量包含 `README.md` 和可运行代码，运行方式统一为在仓库根目录执行：

```bash
uv run <章节脚本>
```

## 学完 tutorials 后还缺什么

基础教程覆盖了 AI 应用的主要概念，但生产项目还需要更多工程化能力：

- 架构分层和模块边界
- 文档摄取与知识库增量更新
- 生产级 RAG 检索策略
- LLM 应用测试和回归评估
- 可观测性、日志、trace、用户反馈闭环
- token 成本、性能、限流和缓存
- 前端交互、文件上传、引用展示和工具调用状态
- 后台任务、队列、批处理和定时索引
- Docker、Nginx、数据库、向量库和部署运维

这些内容放在 [../advanced](../advanced/)。

## 建议学习路径

零基础路径：

```text
tools → basic → protocols → transformer → llm_api → prompt → rag → fastapi → langchain → langgraph
```

Agent 路径：

```text
llm_api → prompt → langchain → langgraph → memory → mcp → skills → deepagents → multi_agent
```

RAG 路径：

```text
llm_api → prompt → rag → evaluation → security → local_models → advanced/02_knowledge_engineering → advanced/03_production_rag
```

工程化路径：

```text
fastapi → security → evaluation → capstone → advanced/01_product_architecture → advanced/05_quality_engineering → advanced/09_deployment_operations
```
