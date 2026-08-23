"""ReAct：用 Thought -> Action -> Observation 循环完成问答。

本示例不调用模型 API，而是用规则模拟 Agent 的决策过程，帮助理解 ReAct
的状态流转。

运行（在仓库根目录）：uv run tutorials/21_planning/00_react/main.py
"""

from __future__ import annotations


MAX_STEPS = 4

KNOWLEDGE_BASE = {
    "专业版 价格": "专业版每月 29 元，支持历史版本保留 180 天。",
    "专业版 团队协作": "专业版支持最多 10 个协作者共同编辑笔记。",
    "免费版 设备同步": "免费版支持最多 2 台设备同步。",
}


def search_docs(query: str) -> str:
    """模拟知识库搜索工具。"""
    return KNOWLEDGE_BASE.get(query, "没有找到相关资料。")


def choose_action(question: str, observations: list[str]) -> tuple[str, str] | None:
    """根据已有观察决定下一步工具调用。

    返回 (thought, query)。如果证据已经足够，返回 None。
    """
    joined = "\n".join(observations)
    if "专业版" in question and "多少钱" in question and "每月 29 元" not in joined:
        return "需要先查专业版价格。", "专业版 价格"
    if "团队协作" in question and "协作者" not in joined:
        return "已有价格信息，还需要确认专业版团队协作能力。", "专业版 团队协作"
    return None


def answer(question: str, observations: list[str]) -> str:
    evidence = "\n".join(observations)
    if "每月 29 元" in evidence and "10 个协作者" in evidence:
        return "专业版每月 29 元，支持最多 10 个协作者共同编辑笔记。"
    return "资料不足，无法完整回答。"


def run_react(question: str) -> None:
    observations: list[str] = []
    print(f"Question: {question}\n")

    for step in range(1, MAX_STEPS + 1):
        action = choose_action(question, observations)
        if action is None:
            print("Thought: 已有足够证据，可以回答。")
            break

        thought, query = action
        print(f"Step {step}")
        print(f"Thought: {thought}")
        print(f'Action: search_docs("{query}")')
        observation = search_docs(query)
        observations.append(observation)
        print(f"Observation: {observation}\n")
    else:
        print("Thought: 达到最大步数，停止继续调用工具。")

    print("Final:", answer(question, observations))


def main() -> None:
    run_react("云雀笔记专业版是否支持团队协作？多少钱？")


if __name__ == "__main__":
    main()
