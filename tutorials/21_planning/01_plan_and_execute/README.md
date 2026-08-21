# 01 Plan-and-Execute：先计划，再执行

复杂任务如果直接让模型“边想边做”，很容易遗漏步骤或在错误方向上反复尝试。Plan-and-Execute 模式让 Agent **先一次性输出完整步骤清单**，再按部就班执行，最后汇总结果。

## 本章要点

- **规划 vs ReAct**：ReAct 是“做一步想一步”，Plan-and-Execute 是“先想清全局，再逐步执行”。
- **结构化计划**：用 Pydantic 模型约束模型输出，每个步骤包含 `tool` 和 `tool_input`。
- **执行循环**：LangGraph 条件边判断计划是否执行完毕，执行完进入总结节点。
- **适用边界**：目标稳定、步骤可数时效果好；环境频繁变化时应改用动态重规划（下一章）。

## 运行

```bash
uv run tutorials/21_planning/01_plan_and_execute/main.py
```

输出会打印：

1. 模型生成的执行计划（含每一步要调用的工具和参数）。
2. 每一步的执行结果（航班、酒店、天气等模拟数据）。
3. 模型根据结果生成的最终行程建议。

## 核心概念

- **`planner = model.with_structured_output(Plan)`**：让模型只返回符合 `Plan`  schema 的对象，避免自由文本里藏工具调用。
- **状态字段 `current_step`**：记录执行到第几步，条件边据此决定是继续执行还是进入总结。
- **工具注册表 `TOOLS`**：把工具名映射到 Python 函数，执行节点按名调用，模型只负责“建议”工具。

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 模型生成的 `tool` 不在 `TOOLS` 里 | 提示词没说清楚可用工具 | 在 system prompt / field description 里显式枚举 |
| `tool_input` 参数缺字段 | 结构化输出没约束清楚 | 给 `tool_input` 加示例或更细粒度的 schema |
| 步骤顺序不合理 | 模型对任务理解不够 | 在 prompt 里加“步骤顺序要合理”并给 few-shot |
| 计划太长执行慢 | 任务粒度太细 | 把多个同质步骤合并，或改用分层规划 |

## 练习建议

1. 把 `task` 改成“帮我做一份周末杭州两日游攻略”，增加 `search_attractions`、`search_restaurants` 等工具，看计划是否合理。
2. 把本章的“一次性完整计划”改成“先出大纲，再逐节展开”，体会规划粒度的影响。
3. 给 `Step` 增加 `depends_on: list[int]`，让模型表达步骤依赖关系，再按拓扑顺序执行。
