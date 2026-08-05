"""流水线模式：调研 -> 写作 -> 审校，三个专家节点排成一条直线。

多 Agent 最朴素的形态：步骤固定、无分支无回路时，把任务拆成几个
职责单一的节点，让产出沿 State 单向流动。每个节点是一次独立的 LLM 调用，
提示词各自为政——甚至可以给不同节点配不同模型（本章从简，共用一个）。

需要配置模型（见教程首页）。
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))

# 产品资料（虚构；真实场景里它来自检索或数据库），是各节点共享的事实来源
PRODUCT_FACTS = (
    "云雀笔记·专业版：每月 18 元；笔记数量不限；完整历史版本回溯；"
    "10 台设备同步；每月 500 次 AI 摘要。"
)


class State(TypedDict):
    task: str    # 总任务
    points: str  # 调研员提炼的卖点
    draft: str   # 写手的初稿
    final: str   # 审校的定稿


def researcher(state: State) -> dict:
    """调研员：只从资料里提炼卖点，绝不动笔写文案。"""
    resp = model.invoke(
        f"你是产品调研员。围绕任务从资料中提炼 3 条最有传播力的卖点，"
        f"每条一行、不超过 20 字，只依据资料，不要编造，不要写文案。\n\n"
        f"任务：{state['task']}\n资料：{PRODUCT_FACTS}"
    )
    print(f"【调研】\n{resp.content}\n")
    return {"points": resp.content}


def writer(state: State) -> dict:
    """写手：只根据卖点成文，不管事实核对。"""
    resp = model.invoke(
        f"你是文案写手。根据卖点写一段 100 字左右的产品推广文案，"
        f"语气轻快，面向知识工作者。\n\n卖点：\n{state['points']}"
    )
    print(f"【初稿】\n{resp.content}\n")
    return {"draft": resp.content}


def reviewer(state: State) -> dict:
    """审校：对照资料核对事实、控制字数，直接给出定稿。"""
    resp = model.invoke(
        f"你是审校专家。核对初稿与资料是否一致（数字、权益不能错），"
        f"把文案控制在 100 字左右，直接输出定稿，不要解释。\n\n"
        f"资料：{PRODUCT_FACTS}\n\n初稿：\n{state['draft']}"
    )
    print(f"【定稿】\n{resp.content}\n")
    return {"final": resp.content}


builder = StateGraph(State)
builder.add_node("research", researcher)
builder.add_node("write", writer)
builder.add_node("review", reviewer)

# 一条直线：步骤固定，不需要任何条件边
builder.add_edge(START, "research")
builder.add_edge("research", "write")
builder.add_edge("write", "review")
builder.add_edge("review", END)

graph = builder.compile()


def main():
    task = "为云雀笔记专业版写一段 100 字推广文案并经审校定稿"
    print(f"任务：{task}\n")
    result = graph.invoke({"task": task})
    print(f"最终交付：{result['final']}")


if __name__ == "__main__":
    main()
