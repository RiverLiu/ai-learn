"""交接模式：对话中途把控制权一次性交给另一个 Agent。

与主管模式的"派单-回收"不同，交接（Handoff）是状态里的权力转移：
current_agent 字段一旦被售后节点改写，后续轮次的入口路由直接把对话交给售后——
本章演示：用户表达退款意图后，售前把对话交接给售后，此后即使闲聊也由售后继续。

需要配置模型（见教程首页）。
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


class State(TypedDict):
    question: str       # 本轮用户的话
    answer: str         # 本轮回答
    current_agent: str  # 当前接待方："sales"（售前）或 "after_sale"（售后）——交接就发生在这个字段上
    handoff: bool       # 本轮售前是否嗅到了售后意图


class SalesReply(BaseModel):
    """售前顾问的判断与回复。"""

    handoff: bool = Field(description="用户是否表达退款/售后意图、需要转接售后")
    reply: str = Field(description="给用户的话：转接时为一句转接说明，否则为售前回答，50 字以内")


# 售前专用的模型：返回 SalesReply 对象，handoff 字段就是交接信号
sales_desk = model.with_structured_output(SalesReply)


def sales(state: State) -> dict:
    """售前节点：正常答疑；一旦嗅到退款/售后意图，交出接待权。"""
    result = sales_desk.invoke(
        "你是云雀笔记的售前顾问，负责介绍方案与价格（专业版每月 18 元），语气热情。"
        "若用户表达退款、退订等售后意图，设置 handoff=true 并简短告知将转接售后，"
        "不要自己处理售后问题。\n"
        f"用户：{state['question']}"
    )
    print(f"  [售前] {result.reply}")
    return {"answer": result.reply, "handoff": result.handoff}


def after_sale(state: State) -> dict:
    """售后节点：接管对话，并把 current_agent 改写为售后——交接在状态中完成。"""
    resp = model.invoke(
        "你是云雀笔记的售后专员，负责退款与售后（政策：购买 7 天内可全额退款，原路退回），"
        "语气稳妥，50 字以内。\n"
        f"用户：{state['question']}"
    )
    print(f"  [售后] {resp.content}")
    # 关键：写回 current_agent。此后的轮次由售后继续接待，不再回到售前
    return {"answer": resp.content, "current_agent": "after_sale", "handoff": False}


def entry(state: State) -> str:
    """入口路由：State 里记着谁接待，本轮就直接交给谁。"""
    return state["current_agent"]


def sales_exit(state: State) -> str:
    """售前处理完：有售后意图就去售后节点完成交接，否则本轮结束。"""
    return "after_sale" if state["handoff"] else END


builder = StateGraph(State)
builder.add_node("sales", sales)
builder.add_node("after_sale", after_sale)

builder.add_conditional_edges(START, entry)          # 按状态决定本轮谁接待
builder.add_conditional_edges("sales", sales_exit)   # 售前 -> 可能本轮内交接
builder.add_edge("after_sale", END)

graph = builder.compile()

AGENT_LABELS = {"sales": "售前", "after_sale": "售后"}


def main():
    turns = [
        "专业版一个月多少钱？",                     # 售前接待
        "我上周买的专业版，用不太习惯，想退款",      # 售前嗅到退款意图 -> 交接给售后
        "那先不退了。随便问问，你们周末客服在线吗？",  # 已是售后接待，闲聊也不回到售前
    ]
    # 跨轮保留的 State：current_agent 在里面延续，这就是"交接"的全部载体
    state = {"question": "", "answer": "", "current_agent": "sales", "handoff": False}
    for i, q in enumerate(turns, 1):
        print(f"第 {i} 轮（接待方：{AGENT_LABELS[state['current_agent']]}）")
        print(f"  用户：{q}")
        state["question"] = q
        state = graph.invoke(state)  # invoke 返回完整 State，原样喂给下一轮
        print()


if __name__ == "__main__":
    main()
