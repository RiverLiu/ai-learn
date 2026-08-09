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

## 常见面试题

**Q1：什么时候需要多 Agent？**

参考答案：任务天然有多个角色、阶段或专业分工时适合，如调研、写作、审校或客服转接。

**Q2：Pipeline 模式是什么？**

参考答案：固定顺序流水线，一个 Agent 的输出作为下一个 Agent 的输入，适合流程稳定任务。

**Q3：Supervisor 模式是什么？**

参考答案：主管 Agent 根据任务动态分派给不同子 Agent，适合任务类型不固定的场景。

**Q4：Handoff 模式是什么？**

参考答案：当前 Agent 把对话控制权交给另一个 Agent，适合客服从售前转售后。

**Q5：多 Agent 的主要风险是什么？**

参考答案：成本增加、状态不一致、职责不清、循环调用、错误传播和调试困难。

**Q6：如何设计 Agent 职责边界？**

参考答案：每个 Agent 应有明确输入、输出、工具权限和停止条件，避免多个 Agent 争抢同一职责。

**Q7：多 Agent 如何共享状态？**

参考答案：可通过共享 state、数据库、消息历史或任务结果传递，但要控制可见范围和权限。

**Q8：为什么多 Agent 不一定比单 Agent 好？**

参考答案：拆分会增加协调成本和错误传播，简单任务用单 Agent 或固定链路更稳定。

**Q9：如何评估多 Agent 系统？**

参考答案：既评估最终结果，也评估每个 Agent 的中间输出、路由正确性、工具调用和成本。

**Q10：多 Agent 和 Deep Agents 有什么关系？**

参考答案：Deep Agents 可用子代理处理复杂子任务，多 Agent 模式则更泛化地描述角色协作结构。
