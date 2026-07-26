# 06 LangSmith：追踪与评估

**LangSmith** 是 LangChain 生态的观测与评估平台（独立产品，LangChain 应用不强制使用）。
它回答两个问题：**线上发生了什么**（tracing 观测）和**改动有没有变好**（evaluation 评估）。

## 本章要点

- **零侵入追踪**：只要设置了环境变量，所有 LangChain 组件的调用自动上报，
  在网页端看到树状调用链：每级链、每次模型调用的输入/输出/耗时/token 用量。
- 对非 LangChain 代码（如自写函数），可用 `@traceable` 装饰器纳入同一条 trace。
- **评估（本教程不展开）**：把典型输入和期望答案存成 dataset，用评估器（含"LLM 当裁判"）
  批量打分，对比不同提示词/模型/检索参数的效果——RAG 调参的正规军打法。

## 配置

复制 `.env.example` 为 `.env` 并填入密钥（或 export 同名环境变量）：

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=ls__...    # 在 https://smith.langchain.com 注册创建（有免费额度）
LANGSMITH_PROJECT=ai-guide
```

之后运行**前面任何一章**的代码（不只是本章脚本），trace 都会出现在对应项目里。

## 运行

```bash
uv run tutorials/langchain/06_langsmith/main.py
```

未配置时脚本打印指引；配置后运行一条链，并提示去网页端查看 trace。

## 核心概念

- **先追踪、后评估、再优化**：LLM 应用 Debug 难在"输入输出不确定"，trace 是第一基础设施；
  没有 trace 就没有评估，没有评估就只能靠感觉调提示词。
- LangSmith 是闭源托管服务；同类开源替代有 Langfuse、OpenTelemetry + Phoenix 等，概念相通。
