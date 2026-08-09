# 03 `create_react_agent`：一行构建工具调用 Agent

[langchain 教程第 5 章](../../09_langchain/05_tools/)手写的工具调用循环，在 LangGraph 里
由预建组件 `create_react_agent` 托管。它内部就是一张你已经看得懂的图：

```
        ┌──────────────────────────────┐
        ▼                              │
START → agent（LLM 节点）── 想调工具？ ──→ tools（工具节点）
              │                          （执行后回到 agent）
              └── 不想调 ──→ END
```

"想调工具？"就是第 2 章的条件边：检查 LLM 返回的消息里有没有 `tool_calls`。

## 本章要点

- `create_react_agent(model, tools=[...])`：一行得到编译好的图，
  循环控制、消息追加、异常包装全部托管。
- Agent 的输入输出都是 `{"messages": [...]}`：完整消息历史在 State 里流动。
- `stream_mode="values"` 逐节点观察：能清楚看到 LLM 决策与工具执行交替前进。

## 运行

```bash
uv run tutorials/10_langgraph/03_react_agent/main.py
```

预期输出：`[LLM 决定]` 与 `[工具返回]` 交替出现若干次，最后是 `[最终回答]`。

## 核心概念

- **ReAct（Reason + Act）**：让模型"边推理边行动"的范式，是工具调用 Agent 的经典模式。
- **预建组件 vs 手画图**：`create_react_agent` 覆盖 80% 场景；需要定制
  （审批、多 Agent、特殊分支）时，退回第 1、2 章的原语自己画——第 4 章就是例子。
