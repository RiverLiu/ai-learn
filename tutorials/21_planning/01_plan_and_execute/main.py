"""Plan-and-Execute：先让 Agent 制定结构化计划，再按步骤执行。

核心思路：
1. 把用户目标交给 LLM，让它输出一个“步骤清单”，每个步骤包含要调用的工具和参数；
2. 用一个循环节点按顺序执行计划里的每一步；
3. 最后把所有步骤结果交给 LLM，生成完整回答。

这种方式比纯 ReAct 更有方向感：模型先“想清楚”，再“动手”，
适合步骤可数、目标稳定的中等复杂度任务（行程规划、调研、报告提纲等）。

运行（在仓库根目录）：uv run tutorials/21_planning/01_plan_and_execute/main.py
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
# 1. 模拟工具（真实场景可换成航班/酒店/天气 API）
# ---------------------------------------------------------------------------
def search_flights(origin: str, destination: str, date: str) -> str:
    """查询两个城市之间的航班。"""
    return f"{origin} → {destination}，{date} 有 MU5103（08:30-10:55），经济舱 880 元。"


def search_hotels(city: str, check_in: str, nights: int) -> str:
    """查询城市酒店。"""
    return f"{city} {check_in} 起 {nights} 晚，推荐南京东路亚朵酒店，每晚 450 元。"


def get_weather(city: str, date: str) -> str:
    """查询指定城市某天的天气。"""
    fake = {("上海", "2026-08-10"): "多云 29°C", ("上海", "2026-08-11"): "雷阵雨 27°C"}
    return fake.get((city, date), f"{city} {date} 天气晴好 30°C")


TOOLS = {
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "get_weather": get_weather,
}


# ---------------------------------------------------------------------------
# 2. 结构化计划：模型一次输出步骤清单
# ---------------------------------------------------------------------------
class Step(BaseModel):
    """计划中的单一步骤。"""

    step_number: int = Field(description="步骤序号，从 1 开始")
    action: str = Field(description="这一步要做什么，用一句话描述")
    tool: str = Field(description=f"要调用的工具名，必须是 {list(TOOLS.keys())} 之一")
    tool_input: dict = Field(description="调用工具时传入的参数字典")


class Plan(BaseModel):
    """完整执行计划。"""

    steps: list[Step] = Field(description="完成任务的步骤列表")


planner = model.with_structured_output(Plan)


# ---------------------------------------------------------------------------
# 3. LangGraph 状态
# ---------------------------------------------------------------------------
class State(TypedDict):
    task: str
    plan: list[Step]
    current_step: int
    results: list[str]
    final_answer: str


# ---------------------------------------------------------------------------
# 4. 节点：制定计划
# ---------------------------------------------------------------------------
def plan_node(state: State) -> dict:
    """根据任务生成结构化计划。"""
    prompt = (
        "你是一个严谨的行程规划助手。请为下面这个目标制定一个详细的执行计划。\n"
        "要求：\n"
        "1. 每一步只能调用一个工具；\n"
        f"2. 可用工具：{list(TOOLS.keys())}；\n"
        "3. 每个 Step 必须包含 step_number、action、tool、tool_input 四个字段；\n"
        "4. tool_input 必须是该工具需要的参数；\n"
        "5. 步骤顺序要合理。\n\n"
        "输出示例（假设目标是查北京到上海 8 月 10 日的航班和酒店）：\n"
        '{\n'
        '  "steps": [\n'
        '    {"step_number": 1, "action": "查询北京到上海的航班", "tool": "search_flights", "tool_input": {"origin": "北京", "destination": "上海", "date": "2026-08-10"}},\n'
        '    {"step_number": 2, "action": "查询上海 8 月 10 日的酒店", "tool": "search_hotels", "tool_input": {"city": "上海", "check_in": "2026-08-10", "nights": 2}},\n'
        '    {"step_number": 3, "action": "查询上海 8 月 10 日的天气", "tool": "get_weather", "tool_input": {"city": "上海", "date": "2026-08-10"}}\n'
        '  ]\n'
        '}\n\n'
        f"目标：{state['task']}"
    )
    plan = planner.invoke(prompt)
    return {"plan": plan.steps, "current_step": 0, "results": []}


# ---------------------------------------------------------------------------
# 5. 节点：执行当前步骤
# ---------------------------------------------------------------------------
def execute_node(state: State) -> dict:
    """执行计划中的当前步骤，并记录结果。"""
    step = state["plan"][state["current_step"]]
    tool_func = TOOLS.get(step.tool)

    if tool_func is None:
        result = f"错误：未知工具 {step.tool}"
    else:
        try:
            result = tool_func(**step.tool_input)
        except Exception as exc:
            result = f"工具调用失败：{exc}"

    results = state["results"] + [f"步骤 {step.step_number}（{step.action}）：{result}"]
    return {"results": results, "current_step": state["current_step"] + 1}


# ---------------------------------------------------------------------------
# 6. 条件路由：还没执行完就继续，执行完了就总结
# ---------------------------------------------------------------------------
def route_after_execute(state: State) -> str:
    if state["current_step"] < len(state["plan"]):
        return "execute"
    return "summarize"


# ---------------------------------------------------------------------------
# 7. 节点：总结最终回答
# ---------------------------------------------------------------------------
def summarize_node(state: State) -> dict:
    """把所有步骤结果汇总成最终回答。"""
    prompt = (
        f"用户目标：{state['task']}\n\n"
        "以下是按计划执行后得到的结果：\n"
        + "\n".join(state["results"])
        + "\n\n请根据以上结果给出完整、清晰的最终回答。"
    )
    resp = model.invoke(prompt)
    return {"final_answer": resp.content}


# ---------------------------------------------------------------------------
# 8. 组装图
# ---------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("plan", plan_node)
builder.add_node("execute", execute_node)
builder.add_node("summarize", summarize_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "execute")
builder.add_conditional_edges(
    "execute",
    route_after_execute,
    {"execute": "execute", "summarize": "summarize"},
)
builder.add_edge("summarize", END)

graph = builder.compile()


# ---------------------------------------------------------------------------
def main():
    task = "帮我规划 2026-08-10 从北京去上海出差 2 天的行程，包括航班、酒店和天气。"
    print(f"任务：{task}\n")

    state = graph.invoke({"task": task})

    print("=== 执行计划 ===")
    for step in state["plan"]:
        print(f"  {step.step_number}. {step.action} → {step.tool}({step.tool_input})")
    print()

    print("=== 各步骤结果 ===")
    for r in state["results"]:
        print(r)

    print("\n=== 最终回答 ===")
    print(state["final_answer"])


if __name__ == "__main__":
    main()
