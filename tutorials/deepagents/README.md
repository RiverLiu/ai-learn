# Deep Agents 教程

Deep Agents（`deepagents` 包）是 LangChain 官方基于 LangGraph 构建的**深度代理框架**。
[langgraph 教程](../langgraph/)的 ReAct Agent 擅长"来回几轮解决问题"；Deep Agent 面向的是
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
[langgraph 教程](../langgraph/)学到的 streaming、interrupt、持久化，原样适用。

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

各章需要模型（配置方式同 [langchain 教程](../langchain/README.md#模型配置)，
根目录 `.env` 或环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`）。
Deep Agent 会连续发起多轮工具调用，建议用能力较强的模型。

## 参考

- 官方文档：https://docs.langchain.com/oss/python/deepagents/overview
- 仓库：https://github.com/langchain-ai/deepagents
