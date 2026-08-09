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

## 常见面试题

**Q1：LangGraph 相比链式调用解决了什么？**

参考答案：它适合有状态、循环、条件分支、人机协作和可恢复执行的 Agent 流程。

**Q2：State、Node、Edge 分别是什么？**

参考答案：State 是图共享状态，Node 是处理函数，Edge 定义节点间流转关系。

**Q3：条件边有什么用？**

参考答案：条件边根据当前状态决定下一步去哪，适合路由、循环、重试和工具调用判断。

**Q4：Checkpointer 的作用是什么？**

参考答案：保存图执行状态，使多轮对话、暂停恢复和失败恢复成为可能。

**Q5：Human-in-the-loop 为什么重要？**

参考答案：高风险工具调用或不确定决策需要人工确认，避免模型直接执行危险动作。

**Q6：ReAct Agent 的核心循环是什么？**

参考答案：模型思考下一步、调用工具、观察结果，再继续推理，直到给出最终答案。

**Q7：如何防止 Agent 死循环？**

参考答案：设置最大步数、超时、工具调用次数限制和失败兜底策略。

**Q8：LangGraph 中 thread_id 有什么作用？**

参考答案：thread_id 用来区分会话或执行线程，让 checkpointer 能读取和保存对应状态。

**Q9：为什么图状态要设计得克制？**

参考答案：状态过大或混乱会增加序列化、调试和上下文管理成本，应只保存必要信息。

**Q10：LangGraph 适合所有 LLM 应用吗？**

参考答案：不适合。简单单轮问答或固定链路用普通函数或 LCEL 更简单；复杂 Agent 才需要图。
