"""主管模式：一个 supervisor 节点负责分派，worker 节点各管一摊。

步骤不固定、每轮都要判断"这事该谁办"时，把判断集中到一个 supervisor：
它自己不答题，只用结构化输出给出分派决定；路由函数把决定翻译成节点名——
这正是 langgraph 教程第 2 章的条件边，只是路由依据从"文本检查"换成了"LLM 判断"。

与 deepagents 教程第 3 章的 task 子代理同源：那里框架托管、子代理上下文隔离；
这里徒手实现同一原理，worker 是共享 State 的单次调用节点。

需要配置模型（见教程首页）。
"""

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))

# 分派目标 -> 展示名
WORKERS = {"price": "查价员", "refund": "退款员", "chat": "闲聊员"}


class State(TypedDict):
    question: str  # 用户问题
    route: str     # supervisor 的分派结果
    answer: str    # worker 的回答


class Dispatch(BaseModel):
    """supervisor 的分派决定：Literal 限定取值，结果可解析、可校验。"""

    target: Literal["price", "refund", "chat"] = Field(
        description="派给谁：price=查价员，refund=退款员，chat=闲聊员"
    )


# 主管专用的模型：只会返回 Dispatch 对象，不会返回自由文本
dispatcher = model.with_structured_output(Dispatch)


def supervisor(state: State) -> dict:
    """主管：只判断该派给谁，自己绝不回答。"""
    decision = dispatcher.invoke(
        "你是客服主管，根据用户问题决定派给哪个专员，自己不回答。判定标准：\n"
        "- price：咨询价格、方案对比\n"
        "- refund：退款、退订等售后诉求\n"
        "- chat：问候、闲聊等与业务无关的话\n"
        f"用户问题：{state['question']}"
    )
    print(f"  [主管] 分派 -> {WORKERS[decision.target]}")
    return {"route": decision.target}


def route(state: State) -> str:
    """路由函数：把 supervisor 的决定翻译成节点名（对照 langgraph 02 章）。"""
    return {"price": "price_worker", "refund": "refund_worker", "chat": "chat_worker"}[
        state["route"]
    ]


# 三个 worker：同一个模型，不同人设，各管一摊
def price_worker(state: State) -> dict:
    """查价员：只答价格与方案问题。"""
    resp = model.invoke(
        "你是云雀笔记的查价员，只回答价格与方案问题，50 字以内。"
        "资料：专业版每月 18 元；团队版每成员每月 45 元、5 人起购。\n"
        f"用户问题：{state['question']}"
    )
    print(f"  [查价员] {resp.content}")
    return {"answer": resp.content}


def refund_worker(state: State) -> dict:
    """退款员：只处理退款与售后。"""
    resp = model.invoke(
        "你是云雀笔记的退款专员，说明退款政策与流程，50 字以内。"
        "政策：购买 7 天内可全额退款，原路退回。\n"
        f"用户问题：{state['question']}"
    )
    print(f"  [退款员] {resp.content}")
    return {"answer": resp.content}


def chat_worker(state: State) -> dict:
    """闲聊员：陪聊，不谈业务。"""
    resp = model.invoke(
        "你是闲聊员，陪用户轻松聊两句，不涉及业务，50 字以内。\n"
        f"用户问题：{state['question']}"
    )
    print(f"  [闲聊员] {resp.content}")
    return {"answer": resp.content}


builder = StateGraph(State)
builder.add_node("supervisor", supervisor)
builder.add_node("price_worker", price_worker)
builder.add_node("refund_worker", refund_worker)
builder.add_node("chat_worker", chat_worker)

builder.add_edge(START, "supervisor")
# 条件边：supervisor 执行完后，由路由函数决定去哪个 worker
builder.add_conditional_edges("supervisor", route)
# 一次性问答：worker 答完即结束（需要"汇报后再分派"时，把边指回 supervisor 即成循环）
builder.add_edge("price_worker", END)
builder.add_edge("refund_worker", END)
builder.add_edge("chat_worker", END)

graph = builder.compile()


def main():
    questions = [
        "专业版多少钱？",                       # 预期 -> 查价员
        "我上周买的专业版，用不习惯，想退款",     # 预期 -> 退款员
        "今天天气真不错，随便聊聊吧",            # 预期 -> 闲聊员
    ]
    for q in questions:
        print(f"用户：{q}")
        graph.invoke({"question": q})
        print()


if __name__ == "__main__":
    main()
