"""RAG failure diagnosis demo.

Run:
    uv run advanced/03_production_rag/01_failure_diagnosis/main.py
"""

from __future__ import annotations


CONTEXT_LIMIT = 2

QUESTION = "企业版支持 SSO 吗？"

RETRIEVED = [
    {
        "chunk_id": "faq:login",
        "score": 0.82,
        "text": "云雀笔记支持手机号、邮箱和第三方账号登录。",
    },
    {
        "chunk_id": "pricing:enterprise",
        "score": 0.77,
        "text": "企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。",
    },
    {
        "chunk_id": "intro:security",
        "score": 0.73,
        "text": "云雀笔记提供权限管理、数据加密和团队协作能力。",
    },
]

MODEL_ANSWER = "支持，所有版本都支持 SSO。"
EXPECTED_FACTS = {"企业版支持 SSO", "个人版和团队版不包含 SSO"}
FORBIDDEN_FACTS = {"所有版本都支持 SSO"}


def diagnose() -> str:
    context = RETRIEVED[:CONTEXT_LIMIT]
    context_text = "\n".join(item["text"] for item in context)
    has_evidence = all(fact in context_text for fact in EXPECTED_FACTS)
    has_forbidden_answer = any(fact in MODEL_ANSWER for fact in FORBIDDEN_FACTS)

    if not any(item["chunk_id"] == "pricing:enterprise" for item in RETRIEVED):
        return "无召回：正确 chunk 没有出现在 Top-K。"
    if not any(item["chunk_id"] == "pricing:enterprise" for item in context):
        return "召回有但被截断：正确 chunk 排名不够靠前，没有进入上下文。"
    if has_evidence and has_forbidden_answer:
        return "上下文有但回答错：优先修 prompt、忠实度检查和评估样本。"
    return "检索和生成都通过，继续看答案完整性、引用和用户反馈。"


def main() -> None:
    print(f"问题：{QUESTION}\n")
    print("Top-K 检索结果：")
    for rank, item in enumerate(RETRIEVED, start=1):
        print(f"{rank}. {item['chunk_id']} score={item['score']}")

    print(f"\n进入上下文的前 {CONTEXT_LIMIT} 条：")
    for item in RETRIEVED[:CONTEXT_LIMIT]:
        print(f"- [{item['chunk_id']}] {item['text']}")

    print(f"\n模型答案：{MODEL_ANSWER}")
    print(f"诊断结论：{diagnose()}")


if __name__ == "__main__":
    main()
