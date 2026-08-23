"""Reflection：生成初稿后自我检查，再修订。

本示例不调用模型 API，用规则模拟 Draft -> Critique -> Revise -> Final。

运行（在仓库根目录）：uv run tutorials/21_planning/05_reflection/main.py
"""

from __future__ import annotations


QUESTION = "专业版多少钱？支持多少协作者？"
EVIDENCE = [
    "专业版每月 29 元。",
    "专业版支持最多 10 个协作者共同编辑笔记。",
]
REQUIRED_FACTS = ["每月 29 元", "10 个协作者"]


def draft_answer() -> str:
    """故意生成一个漏项初稿，用于演示 reflection。"""
    return "专业版每月 29 元。"


def critique(answer: str) -> list[str]:
    issues = []
    for fact in REQUIRED_FACTS:
        if fact not in answer:
            issues.append(f"缺少事实：{fact}")
    if "根据资料" not in answer:
        issues.append("缺少证据约束说明。")
    return issues


def revise(answer: str, issues: list[str]) -> str:
    revised = answer
    if any("10 个协作者" in issue for issue in issues):
        revised = "专业版每月 29 元，支持最多 10 个协作者共同编辑笔记。"
    if any("证据约束" in issue for issue in issues):
        revised = f"根据资料，{revised}"
    return revised


def main() -> None:
    print(f"Question: {QUESTION}\n")
    print("Evidence:")
    for item in EVIDENCE:
        print(f"- {item}")

    draft = draft_answer()
    print(f"\nDraft: {draft}")

    issues = critique(draft)
    print("\nCritique:")
    for issue in issues:
        print(f"- {issue}")

    final = revise(draft, issues)
    print(f"\nFinal: {final}")


if __name__ == "__main__":
    main()
