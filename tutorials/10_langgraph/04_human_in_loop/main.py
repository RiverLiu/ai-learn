"""interrupt 人工审批：让图在关键节点暂停，等人拍板后再继续。

模型只"提议"、不"执行"（langchain 教程第 5 章），那么危险动作谁来把关？
interrupt 原语：节点内调用它，图立即暂停并把问题抛给调用方；
调用方用 Command(resume=...) 把人的决定送回，图从暂停处继续。

本章不调用 LLM（审批逻辑与模型无关），直接运行即可。
"""

from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    action: str   # 待执行的操作
    amount: int   # 金额
    approved: bool
    result: str


def ask_approval(state: State) -> dict:
    """审批节点：interrupt 让图在此暂停，等待人工输入。"""
    decision = interrupt(
        {
            "question": f"即将执行「{state['action']} {state['amount']} 元」，是否批准？",
            "options": ["yes", "no"],
        }
    )
    # 恢复时，interrupt 的返回值就是 Command(resume=...) 传入的值
    return {"approved": decision == "yes"}


def execute(state: State) -> dict:
    return {"result": f"已执行：{state['action']} {state['amount']} 元"}


def reject(state: State) -> dict:
    return {"result": "已取消：操作未获批准"}


def route(state: State) -> str:
    return "execute" if state["approved"] else "reject"


builder = StateGraph(State)
builder.add_node("ask_approval", ask_approval)
builder.add_node("execute", execute)
builder.add_node("reject", reject)
builder.add_edge(START, "ask_approval")
builder.add_conditional_edges("ask_approval", route)
builder.add_edge("execute", END)
builder.add_edge("reject", END)

# interrupt 需要 checkpointer 保存暂停时的现场，才能之后恢复
graph = builder.compile(checkpointer=MemorySaver())


def main():
    config = {"configurable": {"thread_id": "demo-1"}}  # 一次执行 = 一个线程

    # 第一次调用：图执行到 interrupt 就暂停，返回值中带 __interrupt__
    paused = graph.invoke({"action": "转账", "amount": 5000}, config=config)
    question = paused["__interrupt__"][0].value
    print(f"图已暂停，等待人工审批：{question['question']}{question['options']}")

    # 模拟人批准：用同一个 thread_id 恢复执行
    final = graph.invoke(Command(resume="yes"), config=config)
    print(f"批准之后：{final['result']}")

    # 换一个线程演示"拒绝"分支
    paused = graph.invoke({"action": "删除全部数据", "amount": 0}, {"configurable": {"thread_id": "demo-2"}})
    print(f"\n图已暂停，等待人工审批：{paused['__interrupt__'][0].value['question']}")
    final = graph.invoke(Command(resume="no"), config={"configurable": {"thread_id": "demo-2"}})
    print(f"拒绝之后：{final['result']}")


if __name__ == "__main__":
    main()
