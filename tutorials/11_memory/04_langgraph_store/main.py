"""LangGraph Store：框架级的长期记忆，与 checkpointer 的分工协作。

- checkpointer：短期记忆，按 thread_id 存"这个会话聊了什么"（langgraph 教程第 5 章）；
- Store：长期记忆，按 namespace 存"这个用户是什么样的人"，跨会话共享。

本章三部分：
1. Store 的增删查与 namespace 隔离（无需密钥）；
2. 给 Store 加向量索引，语义召回（需 Embeddings）；
3. 接入状态图：节点从 Store 读记忆注入模型，checkpointer 同时管短期历史（需模型）。
"""

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

load_dotenv()


def demo_crud():
    """Store 基础：put/get/search，namespace 天然支持多用户隔离。"""
    print("===== 1. Store 增删查与 namespace 隔离 =====")
    store = InMemoryStore()  # 内存实现；生产换 PostgresStore 等持久化实现
    ns1, ns2 = ("memories", "user-1"), ("memories", "user-2")

    store.put(ns1, "diet", {"data": "不吃辣"})
    store.put(ns1, "job", {"data": "后端工程师，写 Python"})
    store.put(ns2, "diet", {"data": "无辣不欢"})

    print("user-1 全部记忆：", [item.value["data"] for item in store.search(ns1)])
    print("user-2 的 diet：", store.get(ns2, "diet").value["data"])  # 同名 key 互不干扰


def demo_semantic():
    """给 Store 配向量索引后，search(query=...) 按语义排序。"""
    print("\n===== 2. 语义召回 =====")
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
                                  check_embedding_ctx_length=False)
    store = InMemoryStore(index={"dims": 1536, "embed": embeddings})

    ns = ("memories", "user-1")
    store.put(ns, "diet", {"data": "不吃辣，在减脂"})
    store.put(ns, "job", {"data": "后端工程师，写 Python"})
    store.put(ns, "pet", {"data": "养了一只叫年糕的猫"})

    for item in store.search(ns, query="晚餐吃点什么", limit=2):
        print(f"  召回：{item.value['data']}")


def demo_in_graph():
    """Store 进图：节点经 runtime.store 读记忆注入模型；checkpointer 管会话历史。"""
    print("\n===== 3. 接入状态图（Store 长期 + checkpointer 短期） =====")

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str

    model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))

    def chatbot(state: State, runtime: Runtime) -> dict:
        ns = ("memories", state["user_id"])
        recalled = runtime.store.search(ns, query=state["messages"][-1].content, limit=3)
        memory_text = "；".join(item.value["data"] for item in recalled)
        print(f"  （召回记忆：{memory_text or '无'}）")

        system = SystemMessage(content=f"你是贴心的中文助手。关于这位用户，你记得：{memory_text}")
        return {"messages": [model.invoke([system] + state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    # 同一个 Store 对象预置记忆；checkpointer 与 store 各管各的
    store = InMemoryStore()
    store.put(("memories", "user-1"), "diet", {"data": "不吃辣，在减脂"})
    graph = builder.compile(checkpointer=MemorySaver(), store=store)

    config = {"configurable": {"thread_id": "session-1"}}
    result = graph.invoke(
        {"messages": [HumanMessage(content="推荐今晚的晚餐？")], "user_id": "user-1"},
        config=config,
    )
    print(f"  助手：{result['messages'][-1].content}")


def main():
    demo_crud()       # 无需密钥
    demo_semantic()   # 需 Embeddings
    demo_in_graph()   # 需模型


if __name__ == "__main__":
    main()
