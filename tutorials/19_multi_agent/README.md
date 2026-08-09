# 多 Agent 设计模式

学完 [langgraph 教程](../10_langgraph/)的图原语和 [deepagents 教程](../14_deepagents/)的
框架托管协作之后，退一步做**模式提炼**：多 Agent 系统翻来覆去就是三种控制流。
本模块用徒手画的小图把三种模式各实现一遍——理解了原理，用不用框架都只是选型问题。

## 三种模式速览

| 模式 | 一句话 | 控制流 |
| --- | --- | --- |
| 流水线（Pipeline） | 步骤固定，专家节点排成直线 | 无分支无回路 |
| 主管（Supervisor） | 中枢节点每轮决定派给谁 | 星型分发，可成循环 |
| 交接（Handoff） | 对话中途一次性转移控制权 | 状态驱动，不回头 |

## 章节目录

1. [01_pipeline](./01_pipeline/)：流水线模式——调研 → 写作 → 审校
2. [02_supervisor](./02_supervisor/)：主管模式——徒手实现框架托管的"派单"
3. [03_handoff](./03_handoff/)：交接模式——客服对话中的角色转接（含三模式对比与选型）

## 环境准备

```bash
uv sync   # langgraph / langchain-openai 已在项目依赖中
```

三章都调用真实模型，配置方式同 [langchain 教程](../09_langchain/README.md#模型配置)
（根目录 `.env` 或环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`）。

## 参考

- LangGraph Multi-agent 文档：https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- 前置教程：[langgraph 教程](../10_langgraph/)、[deepagents 教程](../14_deepagents/)
