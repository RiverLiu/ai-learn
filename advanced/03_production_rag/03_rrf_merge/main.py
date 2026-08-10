"""Reciprocal Rank Fusion demo.

Run:
    uv run advanced/03_production_rag/03_rrf_merge/main.py
"""

from __future__ import annotations

from collections import defaultdict


RRF_K = 60

VECTOR_RESULTS = [
    "faq:login",
    "pricing:enterprise",
    "intro:security",
    "errors:e1024",
]

KEYWORD_RESULTS = [
    "pricing:enterprise",
    "errors:e1024",
    "faq:sso",
    "intro:security",
]


def reciprocal_rank_fusion(result_lists: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    scores: dict[str, float] = defaultdict(float)
    for results in result_lists:
        for rank, chunk_id in enumerate(results, start=1):
            scores[chunk_id] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def main() -> None:
    print("向量检索排名：")
    for rank, chunk_id in enumerate(VECTOR_RESULTS, start=1):
        print(f"{rank}. {chunk_id}")

    print("\n关键词检索排名：")
    for rank, chunk_id in enumerate(KEYWORD_RESULTS, start=1):
        print(f"{rank}. {chunk_id}")

    print("\nRRF 融合后：")
    for rank, (chunk_id, score) in enumerate(reciprocal_rank_fusion([VECTOR_RESULTS, KEYWORD_RESULTS]), start=1):
        print(f"{rank}. {chunk_id} rrf_score={score:.4f}")


if __name__ == "__main__":
    main()
