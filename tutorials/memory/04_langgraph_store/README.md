# 04 LangGraph Store：框架级长期记忆

前三章手写的机制，LangGraph 用两个内建设施分别接管——分工一句话：
**checkpointer 管"这个会话聊了什么"（短期），Store 管"这个用户是什么样的人"（长期）。**

## 本章要点

- **Store 基本操作**：`put(namespace, key, {"data": ...})` / `get` / `search`。
  namespace 是元组，约定 `("memories", user_id)`——多用户隔离是接口级能力，不用自己拼 key。
- **语义索引**：`InMemoryStore(index={"dims": ..., "embed": ...})` 之后，
  `search(ns, query=..., limit=k)` 就是第 3 章手写的语义召回。
- **进图**：节点签名加 `runtime: Runtime`，通过 `runtime.store` 访问 Store；
  编译时 `compile(checkpointer=..., store=...)` 同时挂上两套记忆，互不干扰。

## 运行

第 1 部分无需密钥；第 2、3 部分需要 Embeddings / 模型：

```bash
uv run tutorials/memory/04_langgraph_store/main.py
```

## 核心概念

- **写入在哪发生**：本章演示的是"读取注入"。写入侧同样走 Store——
  常见做法是一个单独节点在回合结束后做事实抽取（第 2 章的 `extract_facts`）再 `put`，
  或用预建的 [langmem](https://github.com/langchain-ai/langmem) 库托管这套逻辑。
- **生产替换**：`InMemoryStore` 进程退出即失；换 `PostgresStore` 等持久化实现，
  接口不变——与手写教程里"JSON 文件换数据库"是同一层抽象。
- 记忆教程到此闭环：短期（第 1 章）→ 长期闭环（第 2 章）→ 规模化召回（第 3 章）
  → 框架托管（本章）。
