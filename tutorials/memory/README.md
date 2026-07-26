# Memory（记忆）教程

LLM 本身是无状态的：每次调用都不记得上一次。用户却期望助手"记得我"——
记住我的名字、偏好、上周聊到哪。**记忆系统就是给无状态的模型外挂状态。**

## 记忆的两种时间尺度

| | 短期记忆（Short-term） | 长期记忆（Long-term） |
| --- | --- | --- |
| 范围 | 当前会话内 | 跨会话、跨天、永久 |
| 内容 | 对话历史 | 用户画像、偏好、重要事实 |
| 典型实现 | 消息列表 + 截断/摘要 | 抽取 → 存储 → 注入/召回 |
| 对应框架能力 | LangGraph checkpointer | LangGraph Store / 自建存储 |

记忆与 RAG 的关系：RAG 给模型"知识"（文档），记忆给模型"历史"（与这个用户的过往）。
长期记忆的召回环节（第 3 章）与 RAG 检索技术同构，但记忆是**动态生长**的，
多了"何时写、写什么、如何更新与遗忘"的问题。

## 记忆系统的四个设计问题

1. **写入**：什么时候记？（每轮实时 / 会话结束批量 / 用户明示"记住这个"）
2. **内容**：记什么？（偏好、事实、约定值得记；闲聊不值得）
3. **读取**：怎么用？（全量注入 system prompt / 按当前问题语义召回）
4. **维护**：如何更新冲突信息、如何遗忘？（本教程只点到为止）

## 章节目录

1. [01_short_term](./01_short_term/)：短期记忆三策略——完整历史 / 滑动窗口 / 摘要压缩
2. [02_long_term](./02_long_term/)：长期记忆闭环——抽取 → 存储 → 注入
3. [03_semantic_recall](./03_semantic_recall/)：记忆多了之后的语义召回
4. [04_langgraph_store](./04_langgraph_store/)：框架落地——LangGraph Store 与 checkpointer 的分工

## 环境准备

```bash
uv sync
```

第 1～3 章需要模型（配置方式同 [langchain 教程](../langchain/README.md#模型配置)，
在项目根目录放 `.env` 或 export 环境变量）；第 3 章还需要 Embeddings 接口。
第 4 章的 Store 基础用法无需密钥。

## 参考

- LangGraph 记忆文档：https://langchain-ai.github.io/langgraph/concepts/memory/
- 前置教程：[rag](../rag/)（检索技术）、[langgraph](../langgraph/)（第 5 章为短期记忆的框架实现）
