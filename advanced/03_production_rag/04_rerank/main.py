"""Rerank demo with rule-based scoring.

Run:
    uv run advanced/03_production_rag/04_rerank/main.py
"""

from __future__ import annotations


QUESTION = "企业版支持 SSO 吗？其他版本支持吗？"

CANDIDATES = [
    {
        "chunk_id": "intro:security",
        "text": "云雀笔记提供权限管理、数据加密和团队协作能力。",
    },
    {
        "chunk_id": "faq:login",
        "text": "云雀笔记支持手机号、邮箱和第三方账号登录。",
    },
    {
        "chunk_id": "pricing:enterprise",
        "text": "企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。",
    },
    {
        "chunk_id": "security:audit",
        "text": "审计日志会记录成员登录、导出、删除和权限变更操作。",
    },
]


def rerank_score(question: str, text: str) -> int:
    score = 0
    if "SSO" in question and "SSO" in text:
        score += 4
    if "企业版" in question and "企业版" in text:
        score += 3
    if "其他版本" in question and ("个人版" in text or "团队版" in text):
        score += 3
    if "支持" in text:
        score += 1
    return score


def main() -> None:
    print(f"问题：{QUESTION}\n")
    print("第一阶段召回顺序：")
    for rank, item in enumerate(CANDIDATES, start=1):
        print(f"{rank}. {item['chunk_id']} | {item['text']}")

    reranked = sorted(
        CANDIDATES,
        key=lambda item: rerank_score(QUESTION, item["text"]),
        reverse=True,
    )

    print("\nrerank 后：")
    for rank, item in enumerate(reranked, start=1):
        score = rerank_score(QUESTION, item["text"])
        print(f"{rank}. {item['chunk_id']} rerank_score={score} | {item['text']}")

    print("\n进入 LLM 的上下文建议：")
    for item in reranked[:2]:
        print(f"- [{item['chunk_id']}] {item['text']}")


if __name__ == "__main__":
    main()
