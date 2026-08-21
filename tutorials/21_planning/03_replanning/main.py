"""动态重规划：执行过程中遇到意外时，重新评估并调整剩余计划。

核心思路：
1. 先生成一个初始计划；
2. 每执行一步后检查结果；
3. 如果结果表示失败（如“已订满”），就进入 replan 节点，根据已完成结果重新生成剩余步骤；
4. 继续执行新计划，直到完成或达到最大重规划次数。

这种模式适合外部环境不稳定、工具可能失败、用户需求可能变化的长任务。

运行（在仓库根目录）：uv run tutorials/21_planning/03_replanning/main.py
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
# 1. 模拟工具：餐厅预订
# ---------------------------------------------------------------------------
def reserve_table(restaurant: str, date: str, people: int) -> str:
    """预订餐厅，模拟部分热门餐厅会订满。"""
    fully_booked = {"海底捞", "外婆家"}
    if restaurant in fully_booked:
        return f"{restaurant} {date} 已订满，请更换餐厅。"
    return f"成功预订 {restaurant} {date} {people} 人桌。"


TOOLS = {"reserve_table": reserve_table}


# ---------------------------------------------------------------------------
# 2. 结构化计划与重规划输出
# ---------------------------------------------------------------------------
class PlanStep(BaseModel):
    """计划中的单一步骤。"""

    step_number: int = Field(description="步骤序号")
    action: str = Field(description="这一步要做什么")
    tool: str = Field(description=f"工具名，必须是 {list(TOOLS.keys())} 之一")
    tool_input: dict = Field(description="工具参数")


class Plan(BaseModel):
    """初始计划。"""

    steps: list[PlanStep] = Field(description="完成任务的步骤列表")


class ReplanResult(BaseModel):
    """重规划结果。"""

    reason: str = Field(description="为什么要调整计划")
    new_steps: list[PlanStep] = Field(description="调整后的剩余步骤")


planner = model.with_structured_output(Plan)
replaner = model.with_structured_output(ReplanResult)


# ---------------------------------------------------------------------------
# 3. LangGraph 状态
# ---------------------------------------------------------------------------
class State(TypedDict):
    task: str
    plan: list[PlanStep]
    current_step: int
    results: list[str]
    replan_count: int
    final_answer: str


MAX_REPLAN = 3


# ---------------------------------------------------------------------------
# 4. 节点：制定初始计划
# ---------------------------------------------------------------------------
def plan_node(state: State) -> dict:
    prompt = (
        "你是一个餐厅预订助手。请为下面目标制定一个预订计划。\n"
        "注意：热门餐厅（如海底捞、外婆家）很可能订满，请准备备选方案。\n"
        f"可用工具：{list(TOOLS.keys())}\n"
        "每个 Step 必须包含 step_number、action、tool、tool_input 四个字段。\n\n"
        "输出示例：\n"
        '{\n'
        '  "steps": [\n'
        '    {"step_number": 1, "action": "尝试预订海底捞", "tool": "reserve_table", "tool_input": {"restaurant": "海底捞", "date": "2026-08-10", "people": 4}},\n'
        '    {"step_number": 2, "action": "如果海底捞订满，尝试预订西贝", "tool": "reserve_table", "tool_input": {"restaurant": "西贝", "date": "2026-08-10", "people": 4}}\n'
        '  ]\n'
        '}\n\n'
        f"目标：{state['task']}"
    )
    plan = planner.invoke(prompt)
    return {"plan": plan.steps, "current_step": 0, "results": [], "replan_count": 0}


# ---------------------------------------------------------------------------
# 5. 节点：执行当前步骤
# ---------------------------------------------------------------------------
def execute_node(state: State) -> dict:
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
# 6. 条件路由：成功则继续/总结，失败则重规划
# ---------------------------------------------------------------------------
def route_after_execute(state: State) -> str:
    # 计划已全部执行完
    if state["current_step"] >= len(state["plan"]):
        return "summarize"

    # 检查上一步结果是否表示失败
    last_result = state["results"][-1] if state["results"] else ""
    failure_markers = ["已订满", "失败", "不可用", "错误"]
    if any(marker in last_result for marker in failure_markers):
        if state["replan_count"] < MAX_REPLAN:
            return "replan"
        return "summarize"  # 超过最大次数，直接总结

    return "execute"


# ---------------------------------------------------------------------------
# 7. 节点：重规划
# ---------------------------------------------------------------------------
def replan_node(state: State) -> dict:
    """根据已完成结果重新生成剩余步骤。"""
    completed_steps = state["plan"][: state["current_step"]]
    remaining_steps = state["plan"][state["current_step"] :]

    prompt = (
        f"任务：{state['task']}\n\n"
        "已完成的步骤及结果：\n"
        + "\n".join(state["results"])
        + "\n\n"
        "原计划的剩余步骤：\n"
        + "\n".join(f"{s.step_number}. {s.action}" for s in remaining_steps)
        + "\n\n"
        "上一步失败了。请说明失败原因，并给出调整后的剩余步骤（避开已失败的选项）。\n"
        "new_steps 必须是对象列表，每个对象包含 step_number、action、tool、tool_input 四个字段。\n\n"
        "输出示例：\n"
        '{\n'
        '  "reason": "海底捞已订满，需要换一家备选餐厅",\n'
        '  "new_steps": [\n'
        '    {"step_number": 1, "action": "尝试预订西贝", "tool": "reserve_table", "tool_input": {"restaurant": "西贝", "date": "2026-08-10", "people": 4}}\n'
        '  ]\n'
        '}'
    )
    out = replaner.invoke(prompt)

    # 新计划 = 已完成步骤 + 调整后的剩余步骤
    new_plan = completed_steps + out.new_steps
    return {"plan": new_plan, "replan_count": state["replan_count"] + 1}


# ---------------------------------------------------------------------------
# 8. 节点：总结
# ---------------------------------------------------------------------------
def summarize_node(state: State) -> dict:
    prompt = (
        f"用户目标：{state['task']}\n\n"
        "执行过程和结果：\n"
        + "\n".join(state["results"])
        + "\n\n请给出最终回答，说明预订是否成功；如果失败，给出原因和建议。"
    )
    resp = model.invoke(prompt)
    return {"final_answer": resp.content}


# ---------------------------------------------------------------------------
# 9. 组装图
# ---------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("plan", plan_node)
builder.add_node("execute", execute_node)
builder.add_node("replan", replan_node)
builder.add_node("summarize", summarize_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "execute")
builder.add_conditional_edges(
    "execute",
    route_after_execute,
    {"execute": "execute", "replan": "replan", "summarize": "summarize"},
)
builder.add_edge("replan", "execute")
builder.add_edge("summarize", END)

graph = builder.compile()


# ---------------------------------------------------------------------------
def main():
    task = "今晚 19:00 帮我预订一家适合 4 人聚餐的餐厅。"
    print(f"任务：{task}\n")

    state = graph.invoke({"task": task})

    print("=== 最终计划执行轨迹 ===")
    for r in state["results"]:
        print(r)

    print(f"\n重规划次数：{state['replan_count']}")

    print("\n=== 最终回答 ===")
    print(state["final_answer"])


if __name__ == "__main__":
    main()
