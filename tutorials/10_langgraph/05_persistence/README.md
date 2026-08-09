# 05 会话持久化：多轮记忆

LangChain 教程第 1 章说过"多轮对话就是把消息不断追加进列表"——但那个列表当时
是你手动维护的。LangGraph 用 **checkpointer + thread_id** 把这件事变成框架能力。

## 本章要点

- `messages: Annotated[list, add_messages]`：给字段指定 **reducer**，
  节点返回的消息**追加**进历史（默认 reducer 是覆盖）——`add_messages` 还会自动去重。
- `compile(checkpointer=MemorySaver())`：每执行一步就把 State 存档。
  生产环境换 `SqliteSaver` / `PostgresSaver`，接口不变，状态落盘。
- `thread_id` = 一个会话：同一 id 调用自动带历史，不同 id 完全隔离。
- `graph.get_state(config)` 可以查看线程当前存档；还有 `get_state_history`
  回看每一步（时间旅行、从任意历史点分叉重跑，本教程不展开）。

## 运行

```bash
uv run tutorials/10_langgraph/05_persistence/main.py
```

预期输出：`user-1` 线程里助手记得"小明"；`user-2` 线程里则不知道"我"是谁。

## 核心概念

- **Agent 的记忆 = 持久化的 State**：短期记忆（当前会话历史）靠 checkpointer；
  长期记忆（跨会话的用户偏好）需要额外的存储与检索设计（可结合 RAG 教程的思路）。
- 至此本教程覆盖了 Agent 的四大件：**循环**（第 2 章）、**工具**（第 3 章）、
  **人工把关**（第 4 章）、**记忆**（本章）——剩下的都是组合与调优。
