"""分层规划：把复杂任务拆成子任务，逐个完成后再合并成完整结果。

核心思路：
1. 用一个 planner 把大主题拆成若干子任务（subtasks）；
2. 对每个子任务调用同一个 worker（但带着不同提示词）生成片段；
3. 最后把所有片段合并成完整报告/回答。

这种模式适合“分而治之”的任务：技术报告、多维度调研、大型文档写作等。
教学示例为了清晰采用串行 worker；生产环境可用 LangGraph 的 `Send` 把子任务并行分发给多个 worker。

运行（在仓库根目录）：uv run tutorials/21_planning/02_hierarchical_planning/main.py
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


# ---------------------------------------------------------------------------
# 1. 结构化子任务
# ---------------------------------------------------------------------------
class SubTask(BaseModel):
    """大任务拆分后的一个子任务。"""

    title: str = Field(description="子任务标题，也是最终报告的小节名")
    description: str = Field(description="这个子任务具体要写什么内容")


class TaskPlan(BaseModel):
    """分层规划结果。"""

    subtasks: list[SubTask] = Field(description="完成主任务所需的子任务列表，3-5 个为宜")


planner = model.with_structured_output(TaskPlan)


# ---------------------------------------------------------------------------
# 2. LangGraph 状态
# ---------------------------------------------------------------------------
class State(TypedDict):
    topic: str
    subtasks: list[SubTask]
    sections: dict[str, str]
    report: str


# ---------------------------------------------------------------------------
# 3. 节点：拆解任务
# ---------------------------------------------------------------------------
def decompose(state: State) -> dict:
    """把大主题拆成若干子任务。"""
    prompt = (
        "你是一个技术报告规划师。请把下面这个主题拆成 3 个子任务。\n"
        "每个子任务必须包含 title 和 description 两个字段。\n\n"
        "输出示例：\n"
        '{\n'
        '  "subtasks": [\n'
        '    {"title": "asyncio 核心概念", "description": "解释事件循环、协程、Task 的区别与联系"},\n'
        '    {"title": "基本用法示例", "description": "给出 async/await 的典型代码示例"},\n'
        '    {"title": "最佳实践", "description": "总结常见陷阱和性能优化建议"}\n'
        '  ]\n'
        '}\n\n'
        f"主题：{state['topic']}"
    )
    plan = planner.invoke(prompt)
    return {"subtasks": plan.subtasks, "sections": {}}


# ---------------------------------------------------------------------------
# 4. 节点：串行 worker，逐个完成子任务
# ---------------------------------------------------------------------------
def worker_node(state: State) -> dict:
    """为每个子任务生成对应小节内容。"""
    sections = {}
    print("开始分节写作：")
    for sub in state["subtasks"]:
        print(f"  - {sub.title} ...", flush=True)
        prompt = (
            f"主题：{state['topic']}\n"
            f"小节标题：{sub.title}\n"
            f"内容要求：{sub.description}\n\n"
            "请用中文写一段 200-300 字的内容，只输出本节正文，不要加总结性套话。"
        )
        resp = model.invoke(prompt)
        sections[sub.title] = resp.content
    return {"sections": sections}


# ---------------------------------------------------------------------------
# 5. 节点：合并报告
# ---------------------------------------------------------------------------
def compile_node(state: State) -> dict:
    """按子任务顺序合并所有小节，并生成摘要。"""
    print("合并各小节并生成摘要 ...", flush=True)
    ordered = []
    for sub in state["subtasks"]:
        content = state["sections"].get(sub.title, "（本节缺失）")
        ordered.append(f"## {sub.title}\n\n{content}\n")

    body = "\n".join(ordered)
    prompt = (
        f"主题：{state['topic']}\n\n"
        f"以下是各小节内容：\n\n{body}\n\n"
        "请写一段 100 字以内的 executive summary，放在最前面。"
    )
    summary = model.invoke(prompt).content
    report = f"# {state['topic']}\n\n{summary}\n\n{body}"
    return {"report": report}


# ---------------------------------------------------------------------------
# 6. 组装图
# ---------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("decompose", decompose)
builder.add_node("worker", worker_node)
builder.add_node("compile", compile_node)

builder.add_edge(START, "decompose")
builder.add_edge("decompose", "worker")
builder.add_edge("worker", "compile")
builder.add_edge("compile", END)

graph = builder.compile()


# ---------------------------------------------------------------------------
def main():
    topic = "Python asyncio 异步编程入门指南"
    print(f"主题：{topic}\n")

    state = graph.invoke({"topic": topic})

    print("=== 子任务规划 ===")
    for i, sub in enumerate(state["subtasks"], 1):
        print(f"  {i}. {sub.title} —— {sub.description}")

    print("\n=== 生成的报告 ===")
    print(state["report"])


if __name__ == "__main__":
    main()
