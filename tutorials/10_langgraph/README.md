# LangGraph 教程

LangGraph 是 LangChain 生态中的 **Agent 编排框架**。如果说 LangChain/LCEL 是
把组件串成**流水线**（DAG，一路向前），LangGraph 则是把组件组织成**状态机/图**：
可以循环、分支、暂停、恢复——这正是构建 Agent 所需要的。

## 为什么 LCEL 不够用了

| 需求 | LCEL 链 | LangGraph 图 |
| --- | --- | --- |
| 直线流水线（提示词 → 模型 → 解析） | 擅长 | 可以但大材小用 |
| 循环（反复调用工具直到解决） | 表达不了 | 核心能力 |
| 条件分支（按中间结果选路） | 有限（RunnableBranch） | 一等公民 |
| 多轮对话状态 | 手动维护 | 内置 State + Reducer |
| 人工介入（暂停等人审批） | 无 | `interrupt` 原语 |
| 断点续跑 / 崩溃恢复 | 无 | Checkpointer 持久化 |

Agent 的本质就是"LLM 决定下一步 → 执行 → 把结果喂回去 → 再决定"的**循环**，
所以现代 LangChain 官方也推荐用 LangGraph 构建 Agent。

## 章节目录

1. [01_state_graph](./01_state_graph/)：状态图三要素——State、节点、边
2. [02_conditional](./02_conditional/)：条件边与循环——图的灵魂
3. [03_react_agent](./03_react_agent/)：`create_react_agent` 一行构建工具调用 Agent
4. [04_human_in_loop](./04_human_in_loop/)：`interrupt` 人工审批与恢复执行
5. [05_persistence](./05_persistence/)：Checkpointer 会话持久化与多轮记忆

第 1、2、4 章不调用 LLM，无需密钥即可运行；第 3、5 章需要模型（配置方式同
[langchain 教程](../09_langchain/README.md#模型配置)）。

## 环境准备

```bash
uv sync   # langgraph 已在项目依赖中
```

## 参考

- 官方文档：https://langchain-ai.github.io/langgraph/
- 前置教程：[langchain 教程](../09_langchain/)（组件与 LCEL）
