# 04 `interrupt`：人工审批与恢复执行

Agent 越自主，越需要在关键动作前**停下来问人**。LangGraph 把"暂停-等待-恢复"
做成了原语，而不是让开发者自己实现一套状态保存。

## 本章要点

- 节点里调用 `interrupt(payload)`：图**立即暂停**，`payload`（要给用户看的问题）
  随结果的 `__interrupt__` 字段返回给调用方。
- 恢复：用**同一个 `thread_id`** 调用 `graph.invoke(Command(resume=值), config)`，
  图从暂停点继续，且 `interrupt(...)` 的返回值就是这个 `resume` 值。
- **必须配 checkpointer**（本章用 `MemorySaver`）：暂停时的完整 State 靠它保存，
  恢复时原样加载——进程甚至可以在等待期间重启。
- 暂停之后走哪条边，依然是第 2 章条件边说了算：`approved` 进 `execute`，否则进 `reject`。

## 运行

```bash
uv run tutorials/10_langgraph/04_human_in_loop/main.py
```

预期输出：两个演示线程，一个批准（执行转账），一个拒绝（取消删除）。

## 核心概念

- **一次执行 = 一个 thread**：`thread_id` 标识一条执行线，审批等待期间
  别的线程互不影响——这正是多用户系统的隔离方式。
- 真实系统里，两次 `invoke` 之间隔着"把问题推到审批系统 / 等用户点按钮 / Webhook 回调"，
  图的状态一直躺在 checkpointer 里，第 5 章细讲。
