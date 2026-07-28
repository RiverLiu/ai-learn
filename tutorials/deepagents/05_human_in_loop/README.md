# 05 `interrupt_on`：给危险工具加人工审批

Agent 越能干活，越要在关键动作前踩刹车。Deep Agents 不用自己画审批节点
（[langgraph 教程第 4 章](../../langgraph/04_human_in_loop/)的徒手做法），
一个参数就能给指定工具挂上审批点。

## 本章要点

- `interrupt_on={"write_file": True, "edit_file": True}`：这些工具**执行前**图自动暂停，
  `result["__interrupt__"]` 里的 `action_requests` 列出待审批的工具名与参数。
- 恢复：`Command(resume={"decisions": [...]})`，决定与 action_requests 一一对应：
  - `{"type": "approve"}`：照原样执行；
  - `{"type": "edit", "edited_action": {...}}`：**人改完参数再执行**（改文件名、改金额）；
  - `{"type": "reject", "message": "..."}`：拒绝，理由作为工具结果回给 Agent，
    Agent 会读到并调整后续行为。
- 必须配 `checkpointer`（暂停现场的保存与恢复，同 langgraph 教程）。
- `interrupt_on` 也挂在子代理声明里（第 3 章的 SubAgent dict 有同名字段），
  可对子代理的工具分别设卡。

## 运行

```bash
uv run tutorials/deepagents/05_human_in_loop/main.py
```

预期输出：图在写 `/budget.md` 前暂停并打印待审批调用，人工批准后完成写入。

## 核心概念

- **审批点设在"工具执行前"而不是"模型决策后"**：模型可以尽情规划，
  真正动手的那一刻才需要人点头——这是安全与自主性的最佳平衡点。
- 至此五章覆盖了 Deep Agent 的全貌：规划与卸载（1、2 章）、分工（3 章）、
  存储（4 章）、安全（本章）。剩下的就是把它指向你自己的真实工具。
