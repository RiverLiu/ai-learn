# 03 LCEL：用 `|` 组合一切

LCEL（LangChain Expression Language）是 LangChain 的编排核心：所有组件都实现统一的
**Runnable** 接口，用管道符 `|` 连接，前者的输出是后者的输入。

## 本章要点

- **链也是 Runnable**：`prompt | model | parser` 得到的新链照样有 `invoke/stream/batch`，
  可以继续作为更大链路的零件。
- **两级链**：生成 → 加工，中间用 lambda 调整数据形状（dict key 对齐下一级的模板变量）。
- `RunnableLambda`：把任意 Python 函数包成链组件（本地逻辑与 LLM 混排的关键）。
- `RunnableParallel`：同一输入并行喂给多个分支，结果聚合成 dict。

## 运行

```bash
uv run tutorials/09_langchain/03_lcel/main.py
```

## 核心概念

- **统一接口换来免费能力**：只要走 LCEL，流式、批量、异步（`ainvoke`）、
  LangSmith 追踪（第 6 章）全部自动获得，不用为每个功能写适配代码。
- **LCEL 的边界**：LCEL 表达的是无环的数据流水线（DAG）。需要循环、条件分支、
  多轮状态、人工介入时，就该上 LangGraph 了（见 [langgraph 教程](../../10_langgraph/)）。
