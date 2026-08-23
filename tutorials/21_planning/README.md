# Agent Planning：让 Agent 学会“先想后做”

复杂任务不能指望模型“边想边做”还不出错。Planning（规划）是 Agent 先把目标拆成可执行的步骤清单，再按清单推进，必要时根据反馈调整计划。

本模块面向已学完 [LangGraph 基础](../10_langgraph/) 的读者，用五章讲透 Agent 常见的推理、规划、重规划和反思模式。

## CoT 在 Planning 里的位置

CoT（Chain-of-Thought，思维链）是让模型在单次回答中先进行多步推理，再给出答案的提示方法。它已经在 [06_prompt/04_reasoning](../06_prompt/04_reasoning/) 中作为 Prompt 技巧讲过。

在 Agent Planning 里，CoT 更适合作为“内部推理能力”的背景知识，而不是替代外部计划。原因是：

- CoT 主要发生在一次模型调用里，解决“怎么想清楚”。
- Planning 把任务拆成显式步骤，解决“接下来做什么”。
- ReAct 把推理和工具调用交替起来，解决“边观察边行动”。
- Reflection 在结果生成后检查和修订，解决“做完后怎么发现漏项或错误”。

生产环境里也不建议要求模型暴露完整隐藏思维链。更推荐让模型输出：

- 简短理由：说明为什么选择下一步。
- 结构化计划：列出可执行步骤。
- 检查清单：说明最终答案覆盖了哪些约束。
- 可审计轨迹：记录工具调用、观察结果和引用来源。

## 五种 Agent 控制模式

| 模式 | 一句话 | 适用场景 |
| --- | --- | --- |
| **ReAct** | 边想边调用工具，观察结果后继续决策 | 信息不完整、需要边查边判断 |
| **Plan-and-Execute** | 先一次性生成完整计划，再按步骤执行 | 步骤可数、目标稳定的中等复杂度任务 |
| **Hierarchical Planning** | 把大任务拆成子任务，分派给 worker，最后合并 | 报告写作、多维度调研、需要“分而治之” |
| **Replanning** | 执行中监测结果，遇到意外就重新规划剩余步骤 | 外部环境变化、工具可能失败的长任务 |
| **Reflection** | 生成后自我检查，再修订结果 | 答案需要覆盖检查项、格式或事实约束 |

## CoT / ReAct / Planning / Reflection 对比

| 模式 | 核心问题 | 是否调用工具 | 输出形态 |
| --- | --- | --- | --- |
| **CoT** | 这道题如何多步推理？ | 通常不调用 | 答案、简短理由或结构化推理摘要 |
| **ReAct** | 现在该查什么、做什么？ | 调用工具 | Thought / Action / Observation 轨迹 |
| **Plan-and-Execute** | 完成目标需要哪些步骤？ | 按计划调用 | 计划列表 + 执行结果 |
| **Reflection** | 结果哪里不完整或不可靠？ | 可选 | critique + revised answer |

## 前置知识

- Python 基础、Pydantic 模型
- [LangGraph 教程](../10_langgraph/)：状态图、条件边、节点
- [Prompt 教程](../06_prompt/)：结构化输出、few-shot、思维链

## 环境准备

```bash
uv sync
```

各章需要模型（配置方式同 [langchain 教程](../09_langchain/README.md#模型配置)，根目录 `.env` 或环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`）。

规划类任务通常需要多轮调用，建议使用能力较强的模型。

## 章节目录

0. [00_react](./00_react/)：Reason + Act + Observe，边查边判断
1. [01_plan_and_execute](./01_plan_and_execute/)：先制定结构化计划，再逐步执行
2. [02_hierarchical_planning](./02_hierarchical_planning/)：分层拆解 + worker 分治
3. [03_replanning](./03_replanning/)：执行失败时动态调整计划
5. [05_reflection](./05_reflection/)：生成后自我检查与修订

## 学完能做什么

- 用 ReAct 给 Agent 加上“边观察边行动”的工具调用循环。
- 给 Agent 加上“先列 todo 清单”的能力，减少遗漏和重复尝试。
- 把写报告、做调研这类大任务拆成子任务并行/串行处理。
- 在工具调用失败、用户改需求时让 Agent 自动重规划。
- 在生成结果后加入反思检查，减少漏项、格式错误和无证据断言。

## 参考

- Plan-and-Execute paper：[LLM+P](https://arxiv.org/abs/2304.05977)
- LangGraph Multi-agent patterns：https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- ReAct vs Plan-and-Execute：https://blog.langchain.dev/planning-for-agents/
