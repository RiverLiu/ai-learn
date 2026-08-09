from __future__ import annotations

from dataclasses import dataclass


TOP_K = 3


@dataclass(frozen=True)
class RetrievalCase:
    question: str
    expected_chunks: set[str]
    retrieved_chunks: list[str]


@dataclass(frozen=True)
class CitationCase:
    answer: str
    expected_sources: set[str]
    cited_sources: set[str]


RETRIEVAL_CASES = [
    RetrievalCase(
        question="免费版支持多少台设备同步？",
        expected_chunks={"pricing:free"},
        retrieved_chunks=["pricing:free", "faq:sync", "intro:overview"],
    ),
    RetrievalCase(
        question="学生购买专业版有什么优惠？",
        expected_chunks={"pricing:student_discount"},
        retrieved_chunks=["pricing:pro", "pricing:student_discount", "faq:payment"],
    ),
    RetrievalCase(
        question="免费版和专业版的历史版本保留时间有什么区别？",
        expected_chunks={"pricing:free", "pricing:pro"},
        retrieved_chunks=["pricing:free", "faq:export", "pricing:pro"],
    ),
    RetrievalCase(
        question="云雀笔记是否支持 Markdown 导出？",
        expected_chunks={"faq:export"},
        retrieved_chunks=["intro:overview", "faq:share", "faq:export"],
    ),
    RetrievalCase(
        question="企业版是否支持 SSO？",
        expected_chunks={"pricing:enterprise_sso"},
        retrieved_chunks=["pricing:pro", "faq:account", "intro:overview"],
    ),
]


CITATION_CASES = [
    CitationCase(
        answer="免费版支持最多 2 台设备同步。",
        expected_sources={"pricing"},
        cited_sources={"pricing"},
    ),
    CitationCase(
        answer="学生凭 edu 邮箱可申请专业版半价优惠。",
        expected_sources={"pricing"},
        cited_sources={"pricing", "faq"},
    ),
    CitationCase(
        answer="免费版保留 7 天历史版本，专业版保留 180 天。",
        expected_sources={"pricing"},
        cited_sources=set(),
    ),
]


def hit_at_k(case: RetrievalCase, k: int) -> int:
    top_k = set(case.retrieved_chunks[:k])
    return int(bool(case.expected_chunks & top_k))


def recall_at_k(case: RetrievalCase, k: int) -> float:
    top_k = set(case.retrieved_chunks[:k])
    return len(case.expected_chunks & top_k) / len(case.expected_chunks)


def precision_at_k(case: RetrievalCase, k: int) -> float:
    top_k = case.retrieved_chunks[:k]
    if not top_k:
        return 0.0
    return len(case.expected_chunks & set(top_k)) / len(top_k)


def reciprocal_rank(case: RetrievalCase) -> float:
    for index, chunk_id in enumerate(case.retrieved_chunks, start=1):
        if chunk_id in case.expected_chunks:
            return 1 / index
    return 0.0


def citation_precision(case: CitationCase) -> float:
    if not case.cited_sources:
        return 0.0
    return len(case.expected_sources & case.cited_sources) / len(case.cited_sources)


def citation_recall(case: CitationCase) -> float:
    if not case.expected_sources:
        return 1.0
    return len(case.expected_sources & case.cited_sources) / len(case.expected_sources)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def print_retrieval_report() -> None:
    print(f"===== 检索指标（Top-{TOP_K}）=====")
    for case in RETRIEVAL_CASES:
        hit = hit_at_k(case, TOP_K)
        recall = recall_at_k(case, TOP_K)
        precision = precision_at_k(case, TOP_K)
        rr = reciprocal_rank(case)
        print(f"\n问题：{case.question}")
        print(f"期望 chunk：{sorted(case.expected_chunks)}")
        print(f"检索结果：{case.retrieved_chunks[:TOP_K]}")
        print(f"Hit@{TOP_K}: {hit} | Recall@{TOP_K}: {recall:.2f} | Precision@{TOP_K}: {precision:.2f} | RR: {rr:.2f}")

    hits = [hit_at_k(case, TOP_K) for case in RETRIEVAL_CASES]
    recalls = [recall_at_k(case, TOP_K) for case in RETRIEVAL_CASES]
    precisions = [precision_at_k(case, TOP_K) for case in RETRIEVAL_CASES]
    reciprocal_ranks = [reciprocal_rank(case) for case in RETRIEVAL_CASES]

    print("\n===== 检索汇总 =====")
    print(f"Hit Rate@{TOP_K}: {mean(hits):.2f}")
    print(f"Recall@{TOP_K}: {mean(recalls):.2f}")
    print(f"Precision@{TOP_K}: {mean(precisions):.2f}")
    print(f"MRR: {mean(reciprocal_ranks):.2f}")


def print_citation_report() -> None:
    print("\n===== 引用指标 =====")
    for case in CITATION_CASES:
        precision = citation_precision(case)
        recall = citation_recall(case)
        print(f"\n答案：{case.answer}")
        print(f"应引用：{sorted(case.expected_sources)}")
        print(f"实际引用：{sorted(case.cited_sources)}")
        print(f"Citation Precision: {precision:.2f} | Citation Recall: {recall:.2f}")

    precisions = [citation_precision(case) for case in CITATION_CASES]
    recalls = [citation_recall(case) for case in CITATION_CASES]
    print("\n===== 引用汇总 =====")
    print(f"Average Citation Precision: {mean(precisions):.2f}")
    print(f"Average Citation Recall: {mean(recalls):.2f}")


def main() -> None:
    print_retrieval_report()
    print_citation_report()


if __name__ == "__main__":
    main()
