# Agent Planning：让 Agent 学会“先想后做”

复杂任务不能指望模型“边想边做”还不出错。Planning（规划）是 Agent 先把目标拆成可执行的步骤清单，再按清单推进，必要时根据反馈调整计划。

本模块面向已学完 [LangGraph 基础](../10_langgraph/) 的读者，用三章讲透三种最常用的规划模式。

## 三种规划模式

| 模式 | 一句话 | 适用场景 |
| --- | --- | --- |
| **Plan-and-Execute** | 先一次性生成完整计划，再按步骤执行 | 步骤可数、目标稳定的中等复杂度任务 |
| **Hierarchical Planning** | 把大任务拆成子任务，分派给 worker，最后合并 | 报告写作、多维度调研、需要“分而治之” |
| **Replanning** | 执行中监测结果，遇到意外就重新规划剩余步骤 | 外部环境变化、工具可能失败的长任务 |

## 前置知识

- Python 基础、Pydantic 模型
- [LangGraph 教程](../10_langgraph/)：状态图、条件边、节点
- [Prompt 教程](../06_prompt/)：结构化输出、few-shot

## 环境准备

```bash
uv sync
```

各章需要模型（配置方式同 [langchain 教程](../09_langchain/README.md#模型配置)，根目录 `.env` 或环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`）。

规划类任务通常需要多轮调用，建议使用能力较强的模型。

## 章节目录

1. [01_plan_and_execute](./01_plan_and_execute/)：先制定结构化计划，再逐步执行
2. [02_hierarchical_planning](./02_hierarchical_planning/)：分层拆解 + worker 分治
3. [03_replanning](./03_replanning/)：执行失败时动态调整计划

## 学完能做什么

- 给 Agent 加上“先列 todo 清单”的能力，减少遗漏和重复尝试。
- 把写报告、做调研这类大任务拆成子任务并行/串行处理。
- 在工具调用失败、用户改需求时让 Agent 自动重规划。

## 参考

- Plan-and-Execute paper：[LLM+P](https://arxiv.org/abs/2304.05977)
- LangGraph Multi-agent patterns：https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- ReAct vs Plan-and-Execute：https://blog.langchain.dev/planning-for-agents/
