"""Reflection：用评分、批评、修订把初稿改成可交付答案。

本示例不调用模型 API，而是用规则模拟真实业务里的
Draft -> Evaluate -> Critique -> Revise -> Final 流程。

运行（在仓库根目录）：uv run tutorials/21_planning/05_reflection/main.py
"""

from __future__ import annotations

from copy import deepcopy
from typing import TypedDict


QUESTION = "专业版和团队版有什么区别？我适合哪个？"


class EvidenceItem(TypedDict):
    fact_id: str
    source: str
    text: str


EVIDENCE: list[EvidenceItem] = [
    {
        "fact_id": "pro_price",
        "source": "pricing:pro",
        "text": "专业版每月 29 元，支持历史版本保留 180 天。",
    },
    {
        "fact_id": "pro_collaboration",
        "source": "pricing:pro",
        "text": "专业版支持最多 10 个协作者共同编辑笔记。",
    },
    {
        "fact_id": "team_price",
        "source": "pricing:team",
        "text": "团队版每月 99 元，支持最多 50 个成员。",
    },
    {
        "fact_id": "team_admin",
        "source": "faq:team_admin",
        "text": "团队版提供管理员转让、成员权限管理和统一账单。",
    },
    {
        "fact_id": "refund_policy",
        "source": "faq:refund",
        "text": "购买后 7 天内可以申请退款。",
    },
]

REQUIRED_FACTS = {
    "pro_price": "专业版每月 29 元",
    "pro_collaboration": "10 个协作者",
    "team_price": "团队版每月 99 元",
    "team_admin": "管理员转让",
}

FORBIDDEN_UNSUPPORTED_FACTS = ["团队版每月 199 元", "团队版每月 99 元"]


def evidence_by_id(evidence: list[EvidenceItem]) -> dict[str, EvidenceItem]:
    return {item["fact_id"]: item for item in evidence}


def draft_answer() -> str:
    """故意生成一个有漏项、无引用的初稿，用于演示 reflection 的价值。"""
    return "专业版每月 29 元，适合个人使用；团队版适合团队使用。"


def evaluate(answer: str, evidence: list[EvidenceItem]) -> dict[str, int]:
    """给答案打分，总分 10：事实 4、完整性 4、引用 2。"""
    available = evidence_by_id(evidence)
    covered_supported = [
        fact_id
        for fact_id, phrase in REQUIRED_FACTS.items()
        if fact_id in available and phrase in answer
    ]
    missing_supported = [
        fact_id
        for fact_id in REQUIRED_FACTS
        if fact_id in available and REQUIRED_FACTS[fact_id] not in answer
    ]
    unsupported_claims = [
        phrase
        for phrase in FORBIDDEN_UNSUPPORTED_FACTS
        if phrase in answer and not any(phrase in item["text"] for item in evidence)
    ]

    factuality = max(0, 4 - len(unsupported_claims) * 2)
    completeness = min(4, len(covered_supported))
    if missing_supported:
        completeness = min(completeness, 4 - min(len(missing_supported), 4))

    citation_sources = {item["source"] for item in evidence}
    cited_sources = [source for source in citation_sources if f"[{source}]" in answer]
    citation = 2 if len(cited_sources) >= 2 else len(cited_sources)

    total = factuality + completeness + citation
    return {
        "factuality": factuality,
        "completeness": completeness,
        "citation": citation,
        "total": total,
    }


def critique(answer: str, evidence: list[EvidenceItem]) -> list[str]:
    """按事实覆盖、证据不足和引用质量生成可执行问题清单。"""
    available = evidence_by_id(evidence)
    issues: list[str] = []

    for fact_id, phrase in REQUIRED_FACTS.items():
        if fact_id not in available:
            issues.append(f"证据不足：{fact_id}")
        elif phrase not in answer:
            issues.append(f"缺少事实：{fact_id}")

    for phrase in FORBIDDEN_UNSUPPORTED_FACTS:
        if phrase in answer and not any(phrase in item["text"] for item in evidence):
            issues.append(f"无证据支持的断言：{phrase}")

    required_sources = {item["source"] for item in evidence if item["fact_id"] in REQUIRED_FACTS}
    missing_citations = [source for source in sorted(required_sources) if f"[{source}]" not in answer]
    if missing_citations:
        issues.append("缺少引用：" + ", ".join(missing_citations))

    return issues


def revise(answer: str, issues: list[str], evidence: list[EvidenceItem]) -> str:
    """只基于已有 evidence 修订，证据不足时明确说明，不编造。"""
    available = evidence_by_id(evidence)
    parts: list[str] = []

    if "pro_price" in available or "pro_collaboration" in available:
        pro_bits = []
        if "pro_price" in available:
            pro_bits.append(f"{REQUIRED_FACTS['pro_price']} [{available['pro_price']['source']}]")
        if "pro_collaboration" in available:
            pro_bits.append(f"支持最多 {REQUIRED_FACTS['pro_collaboration']}共同编辑 [{available['pro_collaboration']['source']}]")
        parts.append("专业版：" + "，".join(pro_bits) + "。")

    if "team_price" in available or "team_admin" in available:
        team_bits = []
        if "team_price" in available:
            team_bits.append(f"{REQUIRED_FACTS['team_price']} [{available['team_price']['source']}]")
        if "team_admin" in available:
            team_bits.append(f"支持{REQUIRED_FACTS['team_admin']}和成员权限管理 [{available['team_admin']['source']}]")
        parts.append("团队版：" + "，".join(team_bits) + "。")

    missing = [
        fact_id
        for fact_id in REQUIRED_FACTS
        if f"证据不足：{fact_id}" in issues
    ]
    if missing:
        parts.append("资料不足：" + "、".join(missing) + " 暂时不能确认。")

    recommendation = (
        "建议：如果只是个人或小团队协作，优先专业版；如果需要成员权限、管理员转让和统一账单，选择团队版。"
    )
    return "".join(parts + [recommendation])


def run_reflection(
    evidence: list[EvidenceItem] | None = None,
    max_rounds: int = 2,
    target_score: int = 8,
) -> dict:
    """执行多轮 reflection，返回完整轨迹，便于教学观察。"""
    current_evidence = deepcopy(evidence if evidence is not None else EVIDENCE)
    answer = draft_answer()
    history = []

    for round_index in range(max_rounds + 1):
        score = evaluate(answer, current_evidence)
        issues = critique(answer, current_evidence)
        history.append(
            {
                "round": round_index,
                "answer": answer,
                "score": score,
                "issues": issues,
            }
        )
        if score["total"] >= target_score or round_index == max_rounds:
            break
        answer = revise(answer, issues, current_evidence)

    final = history[-1]
    return {
        "question": QUESTION,
        "evidence": current_evidence,
        "history": history,
        "final_answer": final["answer"],
        "final_score": final["score"],
        "final_issues": final["issues"],
    }


def print_score(score: dict[str, int]) -> None:
    print(
        f"Score: factuality={score['factuality']}/4, "
        f"completeness={score['completeness']}/4, citation={score['citation']}/2, "
        f"total={score['total']}/10"
    )


def main() -> None:
    result = run_reflection(max_rounds=2, target_score=8)

    print(f"Question: {result['question']}\n")
    print("Evidence:")
    for item in result["evidence"]:
        print(f"- [{item['source']}] {item['text']}")

    for item in result["history"]:
        label = "Draft" if item["round"] == 0 else f"Reflection Round {item['round']}"
        print(f"\n=== {label} ===")
        print(item["answer"])
        print_score(item["score"])
        if item["issues"]:
            print("Issues:")
            for issue in item["issues"]:
                print(f"- {issue}")
        else:
            print("Issues: none")

    print("\n=== Final Decision ===")
    print(result["final_answer"])

    print("\n=== 反例：证据不足时不能编造 ===")
    missing_team_price = [item for item in EVIDENCE if item["fact_id"] != "team_price"]
    missing_result = run_reflection(evidence=missing_team_price, max_rounds=2, target_score=8)
    print(missing_result["final_answer"])
    print("Remaining issues:")
    for issue in missing_result["final_issues"]:
        print(f"- {issue}")


if __name__ == "__main__":
    main()
