"""条件边与循环：图的灵魂。

LCEL 链只能一路向前；图可以让执行流根据中间结果选择下一条边——
包括"绕回去"形成循环。本章模拟一个"反复打磨文案直到达标"的循环，
不调用 LLM，直接运行即可。
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

MAX_ITERATIONS = 5  # 循环上限：防止无限循环的安全阀


class State(TypedDict):
    draft: str       # 待打磨的文案
    iterations: int  # 已打磨次数


def polish(state: State) -> dict:
    """打磨节点：模拟一次修改（每轮只去掉一处语气词，体现渐进过程）。"""
    text = state["draft"]
    for filler in ("真的", "非常", "特别", "十分"):
        if filler in text:
            text = text.replace(filler, "", 1)  # count=1：每轮最多处理一处
            break
    n = state["iterations"] + 1
    print(f"  第 {n} 轮打磨：{text}")
    return {"draft": text, "iterations": n}


def route(state: State) -> str:
    """路由函数：根据当前 State 决定下一步去哪。

    返回值是下一个节点的名字（或 END）。这就是条件分支的全部。
    """
    has_filler = any(w in state["draft"] for w in ("真的", "非常", "特别", "十分"))
    if has_filler and state["iterations"] < MAX_ITERATIONS:
        return "polish"  # 绕回去，形成循环
    return END           # 达标或到上限，结束


builder = StateGraph(State)
builder.add_node("polish", polish)
builder.add_edge(START, "polish")
# 条件边：polish 执行完后，调用 route 决定去向
builder.add_conditional_edges("polish", route)

graph = builder.compile()


def main():
    result = graph.invoke({"draft": "这个产品真的非常好用，特别值得推荐，十分优秀", "iterations": 0})
    print(f"\n最终文案（{result['iterations']} 轮）：{result['draft']}")


if __name__ == "__main__":
    main()
