"""状态图三要素：State、节点（Node）、边（Edge）。

一个 LangGraph 应用 = 一张有向图：
- State：所有节点共享读写的数据（TypedDict）；
- 节点：普通函数，接收 State，返回"要合并进 State 的更新"（dict）；
- 边：定义执行顺序，START/END 是特殊入口出口节点。

本章不调用 LLM，直接运行即可。
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 1. 定义 State：图中流动的数据。节点返回的 dict 默认覆盖同名字段
class State(TypedDict):
    text: str        # 输入文本
    char_count: int  # 字符数
    label: str       # 分类结果


# 2. 定义节点：接收 State，返回部分更新（只返回要改的字段）
def count_chars(state: State) -> dict:
    """统计字符数。"""
    return {"char_count": len(state["text"])}


def classify(state: State) -> dict:
    """根据字符数打标签（可读取上游节点写入的 char_count）。"""
    label = "长文" if state["char_count"] > 20 else "短文"
    return {"label": label}


# 3. 组装图：添加节点、连接边、编译
builder = StateGraph(State)
builder.add_node("count", count_chars)
builder.add_node("classify", classify)

builder.add_edge(START, "count")       # 入口：先进 count
builder.add_edge("count", "classify")  # count 完成后进 classify
builder.add_edge("classify", END)      # classify 完成后结束

graph = builder.compile()  # 编译成可运行的图


def main():
    # invoke：一次性跑完整张图，返回最终 State
    result = graph.invoke({"text": "LangGraph 让 Agent 编排变成画流程图"})
    print(f"【invoke】{result}")

    # stream：逐节点观察执行过程（每个节点完成后输出一次当前 State）
    print("\n【stream】")
    for step in graph.stream({"text": "短文本"}):
        for node_name, state_update in step.items():
            print(f"  节点 {node_name} 写入：{state_update}")


if __name__ == "__main__":
    main()
