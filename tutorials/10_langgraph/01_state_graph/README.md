# 01 状态图三要素：State、节点、边

LangGraph 把应用建模为一张**有向图**，三个概念撑起全部：

- **State**：一个 `TypedDict`，是图中唯一流动的数据。所有节点读它、写它。
- **节点（Node）**：普通 Python 函数，入参是 State，返回一个 dict 表示
  **要合并进 State 的更新**（默认行为：同名字段直接覆盖）。
- **边（Edge）**：定义节点执行顺序；`START` / `END` 是特殊的入口、出口节点。

`StateGraph(State)` 建图 → `add_node` / `add_edge` 组装 → `compile()` 得到可运行的图。

## 本章要点

- 节点之间**不直接调用**，只靠读写 State 传递数据——这让每个节点可独立替换、独立测试。
- `graph.invoke(state)` 一次跑完返回最终 State；
  `graph.stream(state)` 逐节点输出，是观察图执行的调试利器。
- 本章节点是纯 Python（不调 LLM）：图逻辑与模型无关，这是理解 LangGraph 的正确起点。

## 运行

```bash
uv run tutorials/10_langgraph/01_state_graph/main.py
```

## 核心概念

- **状态合并（Reducer）**：节点返回的 dict 如何并入 State 由字段的 reducer 决定，
  默认"覆盖"；第 5 章的 `messages` 字段会用 `add_messages` reducer 实现"追加"。
- 编译后的图同样是 Runnable：`invoke/stream/batch` 接口与 LCEL 链一致，
  同样可以白嫖 LangSmith 追踪。
