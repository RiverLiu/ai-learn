# 01 第一个 Deep Agent

`create_deep_agent(model, tools, system_prompt)`——入参与 ReAct Agent 几乎一样，
但行为截然不同：接到复杂任务，它会**先列 todo 清单、执行中读写"文件"、最后汇报**。

## 本章要点

- 不需要任何新工具：Deep Agent 的规划（`write_todos`）和文件读写（`write_file` 等）
  是**框架自带的工具**，由中间件注入，与你给的 `tools=[get_weather]` 并列。
- `system_prompt` 给足"工作作风"要求：先计划、结论落盘、口头总结。
  Deep Agents 内部还会叠加一段详尽的内建提示词教它使用这些能力。
- 返回的是**编译好的 LangGraph 图**：`stream/invoke` 用法与 langgraph 教程完全一致。

## 运行

```bash
uv run tutorials/deepagents/01_hello_deep_agent/main.py
```

预期输出：`[决策] write_todos(...)` → `[决策] get_weather(...)` ×2 →
`[决策] write_file(...)` → `[回答] ...`，最后打印状态里的 todos 清单与 files 文件名。

## 核心概念

- **"工作痕迹"在状态里**：运行结束后 `result["todos"]`、`result["files"]` 保留了
  Agent 的计划与产物——这是中间件扩展出来的状态字段，不是消息。
- 本章故意跑了两次同一任务（stream 演示 + invoke 取状态），只为教学直观；
  实际使用一次即可。
- 下一章拆开看这三味药分别是什么、解决什么问题。
