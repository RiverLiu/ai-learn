import importlib.util
import sys
import types
from pathlib import Path


class FakeModel:
    def with_structured_output(self, _schema):
        return self


class FakeStateGraph:
    def __init__(self, _state_type):
        pass

    def add_node(self, *_args, **_kwargs):
        pass

    def add_edge(self, *_args, **_kwargs):
        pass

    def add_conditional_edges(self, *_args, **_kwargs):
        pass

    def compile(self):
        return object()


sys.modules["dotenv"] = types.SimpleNamespace(load_dotenv=lambda: None)
sys.modules["langchain_openai"] = types.SimpleNamespace(ChatOpenAI=lambda **_kwargs: FakeModel())
sys.modules["langgraph"] = types.SimpleNamespace()
sys.modules["langgraph.graph"] = types.SimpleNamespace(END="END", START="START", StateGraph=FakeStateGraph)

MODULE_PATH = Path(__file__).resolve().parents[1] / "tutorials/21_planning/03_replanning/main.py"
spec = importlib.util.spec_from_file_location("replanning_main", MODULE_PATH)
replanning = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(replanning)


def test_route_after_execute_replans_when_last_step_failed():
    state = {
        "task": "订餐",
        "plan": [
            replanning.PlanStep(
                step_number=1,
                action="尝试预订海底捞",
                tool="reserve_table",
                tool_input={"restaurant": "海底捞", "date": "2026-08-23 19:00", "people": 4},
            )
        ],
        "current_step": 1,
        "results": ["步骤 1（尝试预订海底捞）：海底捞 2026-08-23 19:00 已订满，请更换餐厅。"],
        "replan_count": 0,
        "final_answer": "",
    }

    assert replanning.route_after_execute(state) == "replan"


def test_replan_node_resets_current_step_to_first_new_step(monkeypatch):
    class FakeReplanner:
        def invoke(self, _prompt):
            return replanning.ReplanResult(
                reason="海底捞已订满，需要改订西贝",
                new_steps=[
                    replanning.PlanStep(
                        step_number=2,
                        action="尝试预订西贝",
                        tool="reserve_table",
                        tool_input={"restaurant": "西贝", "date": "2026-08-23 19:00", "people": 4},
                    )
                ],
            )

    monkeypatch.setattr(replanning, "replaner", FakeReplanner())
    completed = replanning.PlanStep(
        step_number=1,
        action="尝试预订海底捞",
        tool="reserve_table",
        tool_input={"restaurant": "海底捞", "date": "2026-08-23 19:00", "people": 4},
    )
    remaining = replanning.PlanStep(
        step_number=2,
        action="尝试预订外婆家",
        tool="reserve_table",
        tool_input={"restaurant": "外婆家", "date": "2026-08-23 19:00", "people": 4},
    )
    state = {
        "task": "订餐",
        "plan": [completed, remaining],
        "current_step": 1,
        "results": ["步骤 1（尝试预订海底捞）：海底捞 2026-08-23 19:00 已订满，请更换餐厅。"],
        "replan_count": 0,
        "final_answer": "",
    }

    updates = replanning.replan_node(state)

    assert updates["plan"][0] == completed
    assert updates["plan"][1].tool_input["restaurant"] == "西贝"
    assert updates["current_step"] == 1
    assert updates["replan_count"] == 1
