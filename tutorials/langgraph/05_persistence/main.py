"""会话持久化：checkpointer + thread_id 实现多轮记忆。

图每执行完一步，checkpointer 就把 State 存档；下次用同一 thread_id 调用时
自动载入历史——这就是多轮对话记忆的实现方式。

需要配置模型（见教程首页）。
"""

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class State(TypedDict):
    # add_messages reducer：节点返回的消息"追加"到历史，而不是默认的"覆盖"
    messages: Annotated[list, add_messages]


model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


def chatbot(state: State) -> dict:
    """聊天节点：把完整历史发给模型，返回新回复。"""
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# MemorySaver 把 State 保存在进程内存；生产换 SqliteSaver/PostgresSaver 即落盘
graph = builder.compile(checkpointer=MemorySaver())


def chat(thread_id: str, text: str) -> str:
    """在指定线程上说一句话，返回模型回复。"""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=text)]}, config=config)
    return result["messages"][-1].content


def main():
    # 同一线程：第二轮能记住第一轮说的名字
    print("小明：我叫小明，记住我。")
    print(f"助手：{chat('user-1', '我叫小明，记住我。')}\n")
    print("小明：我叫什么名字？")
    print(f"助手：{chat('user-1', '我叫什么名字？')}\n")

    # 换一个线程：全新会话，不知道"我"是谁
    print("另一个用户：我叫什么名字？")
    print(f"助手：{chat('user-2', '我叫什么名字？')}")

    # 查看 user-1 线程存档的完整状态
    state = graph.get_state({"configurable": {"thread_id": "user-1"}})
    print(f"\nuser-1 线程共存档 {len(state.values['messages'])} 条消息")


if __name__ == "__main__":
    main()
