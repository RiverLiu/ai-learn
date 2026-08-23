# 00 ReAct：边想边做边观察

ReAct 是 Reason + Act 的缩写，核心是让 Agent 在一个循环里交替完成：

```text
Thought -> Action -> Observation -> Thought -> Action -> Observation -> Final
```

它不是先生成完整计划，而是每一步根据当前观察决定下一步做什么。

## 本章要点

- **Thought**：判断当前缺什么信息，决定下一步。
- **Action**：调用一个工具，例如搜索、查询数据库、计算。
- **Observation**：读取工具返回结果。
- **Final**：当证据足够时给出最终回答。

ReAct 适合信息不完整、需要边查边判断的任务；不适合步骤很长、需要严格全局规划的任务。

## 运行

本章是离线示例，不调用模型 API：

```bash
uv run tutorials/21_planning/00_react/main.py
```

## 核心概念

Plan-and-Execute 会先问：

```text
我要完成这个目标，需要哪些步骤？
```

ReAct 会反复问：

```text
我现在知道什么？
我还缺什么？
下一步应该调用哪个工具？
```

所以 ReAct 的优势是灵活，劣势是容易走弯路。生产中通常会给 ReAct 加上最大步数、工具白名单和停止条件。

## 示例流程

任务：

```text
云雀笔记专业版是否支持团队协作？多少钱？
```

Agent 可能先查价格，再发现还需要查功能说明：

```text
Thought: 需要先查专业版价格。
Action: search_docs("专业版 价格")
Observation: 专业版每月 29 元。
Thought: 已有价格，还缺团队协作能力。
Action: search_docs("专业版 团队协作")
Observation: 专业版支持最多 10 个协作者。
Final: 专业版每月 29 元，支持最多 10 个协作者。
```

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 一直调用工具不结束 | 没有停止条件 | 设置最大步数和“证据足够”判断 |
| 工具调用跑偏 | Thought 太泛 | 约束每次 Action 只能解决一个明确问题 |
| 重复搜索同一问题 | 没有记录已查内容 | 在状态里保存 observation history |
| 编造工具结果 | Observation 没有和真实工具绑定 | 工具结果必须由代码返回，不能让模型自由生成 |

## 练习建议

1. 把 `main.py` 里的任务改成“免费版支持几台设备同步？”。
2. 给 `search_docs()` 增加一条新知识，再让 Agent 查询它。
3. 把 `MAX_STEPS` 改成 `1`，观察信息不完整时会发生什么。
