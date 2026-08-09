# Deep Agents 教程

Deep Agents（`deepagents` 包）是 LangChain 官方基于 LangGraph 构建的**深度代理框架**。
[langgraph 教程](../10_langgraph/)的 ReAct Agent 擅长"来回几轮解决问题"；Deep Agent 面向的是
**需要几十步、持续几分钟以上的复杂任务**（深度调研、大型代码改造、多文档报告写作）。

## 为什么 ReAct Agent 不够用

简单 ReAct 循环在复杂任务上的三个短板，恰好是 Deep Agents 内建的三味药：

| 短板 | Deep Agents 的对策 | 对应机制 |
| --- | --- | --- |
| 任务一多就丢三落四，没有计划感 | **显式规划**：把任务清单写进状态，随时更新进度 | `write_todos` 工具（Planning 中间件） |
| 长文档/中间结果塞爆上下文 | **上下文卸载**：把内容写进"文件系统"，需要时再读回 | `write_file`/`read_file`/`edit_file` 等工具（Filesystem 中间件） |
| 一个上下文干所有事，互相干扰 | **子代理隔离**：子任务派给独立上下文的子代理 | `task` 工具（SubAgent 中间件） |

外加一段详尽的系统提示词（教 Agent 如何使用这三件套），组合起来就是 Deep Agent。

## 与 LangChain 生态的关系

```
LangChain（组件）→ LangGraph（编排原语）→ Deep Agents（预建的深度代理）
                                                ↓ 同一张图
                              checkpointer / Store / interrupt 全部可用
```

`create_deep_agent()` 返回的就是一张编译好的 LangGraph 状态图——
[langgraph 教程](../10_langgraph/)学到的 streaming、interrupt、持久化，原样适用。

## 章节目录

1. [01_hello_deep_agent](./01_hello_deep_agent/)：第一个 Deep Agent——看它自己列计划、写文件
2. [02_builtin_capabilities](./02_builtin_capabilities/)：解剖三味药——todos、files、长提示词
3. [03_subagents](./03_subagents/)：子Agent——上下文隔离的分工协作
4. [04_backends](./04_backends/)：文件系统后端——虚拟状态、真实磁盘、持久化 Store
5. [05_human_in_loop](./05_human_in_loop/)：`interrupt_on` 工具审批

本教程基于 **deepagents 0.6.x**（API 变动较快，以安装的版本为准）。

## 环境准备

```bash
uv sync
```

各章需要模型（配置方式同 [langchain 教程](../09_langchain/README.md#模型配置)，
根目录 `.env` 或环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`）。
Deep Agent 会连续发起多轮工具调用，建议用能力较强的模型。

## 参考

- 官方文档：https://docs.langchain.com/oss/python/deepagents/overview
- 仓库：https://github.com/langchain-ai/deepagents

## 常见面试题

**Q1：Deep Agent 解决什么问题？**

参考答案：它面向多步骤、长时间、复杂上下文任务，提供规划、文件系统、子代理和长任务工作流。

**Q2：为什么 ReAct Agent 不够用？**

参考答案：简单 ReAct 容易缺计划、上下文爆炸、职责混乱，复杂任务中难以稳定推进。

**Q3：Deep Agent 的文件系统能力有什么价值？**

参考答案：把中间结果写入外部存储，减少上下文占用，并让过程可追踪、可恢复。

**Q4：子代理有什么价值？**

参考答案：子代理隔离不同子任务上下文，减少相互干扰，适合调研、写作、审校等分工。

**Q5：规划能力为什么重要？**

参考答案：长任务需要显式记录目标、步骤和进度，否则容易遗漏任务或反复尝试。

**Q6：Deep Agent 和 LangGraph 有什么关系？**

参考答案：Deep Agents 基于 LangGraph 构建，返回的是图，仍可使用持久化、interrupt 和 streaming 等能力。

**Q7：什么时候不该用 Deep Agent？**

参考答案：简单问答、固定 RAG 或一次工具调用不需要 Deep Agent，普通链路更简单可靠。

**Q8：长任务如何控制风险？**

参考答案：限制工具权限、记录轨迹、设置步数和时间上限，高风险动作增加人工审批。

**Q9：文件系统后端有哪些选择？**

参考答案：可以是虚拟内存文件系统、真实磁盘或 LangGraph Store，取决于是否需要持久化和跨会话共享。

**Q10：Deep Agent 的主要成本是什么？**

参考答案：多轮推理和工具调用会增加 token、时间和不确定性，需要评估和观测。
