"""Hybrid search demo with no external dependencies.

Run:
    uv run advanced/03_production_rag/02_hybrid_search/main.py
"""

from __future__ import annotations

import math
import re
from collections import Counter


DOCS = [
    {
        "chunk_id": "faq:refund",
        "text": "用户可以在购买后 7 天内申请退款，退款入口位于账单中心。",
        "semantic_tags": {"退款", "退费", "购买", "账单"},
    },
    {
        "chunk_id": "errors:e1024",
        "text": "错误码 E1024 表示上传文件超过大小限制，请压缩文件或升级套餐。",
        "semantic_tags": {"上传", "文件", "大小", "限制"},
    },
    {
        "chunk_id": "errors:s3-timeout",
        "text": "S3UploadTimeout 参数用于控制对象存储上传超时时间。",
        "semantic_tags": {"上传", "对象存储", "超时", "参数"},
    },
    {
        "chunk_id": "pricing:enterprise",
        "text": "企业版支持 SSO、审计日志和专属客户成功经理。",
        "semantic_tags": {"企业", "安全", "登录", "审计"},
    },
]

DOMAIN_TERMS = [
    "退款",
    "错误码",
    "E1024",
    "S3UploadTimeout",
    "SSO",
    "企业版",
    "上传",
    "文件",
    "大小限制",
]

QUERY_TAGS = {
    "怎么退款": {"退款", "退费", "账单"},
    "错误码 E1024 怎么处理": {"错误", "上传", "处理"},
}


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9_]+", lowered)
    for term in DOMAIN_TERMS:
        if term.lower() in lowered:
            tokens.append(term.lower())
    return tokens


def semantic_search(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    query_tags = QUERY_TAGS[query]
    scored = []
    for doc in DOCS:
        overlap = len(query_tags & doc["semantic_tags"])
        union = len(query_tags | doc["semantic_tags"])
        scored.append((doc["chunk_id"], overlap / union))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]


def keyword_search(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    query_terms = tokenize(query)
    doc_terms = [tokenize(doc["text"]) for doc in DOCS]
    document_frequency = Counter(term for terms in doc_terms for term in set(terms))
    scores = []
    for doc, terms in zip(DOCS, doc_terms, strict=True):
        score = 0.0
        counts = Counter(terms)
        for term in query_terms:
            if counts[term] == 0:
                continue
            idf = math.log((len(DOCS) + 1) / (document_frequency[term] + 1)) + 1
            score += counts[term] * idf
        scores.append((doc["chunk_id"], score))
    return sorted(scores, key=lambda item: item[1], reverse=True)[:top_k]


def print_results(title: str, results: list[tuple[str, float]]) -> None:
    print(title)
    for rank, (chunk_id, score) in enumerate(results, start=1):
        print(f"{rank}. {chunk_id} score={score:.3f}")


def main() -> None:
    for query in ["怎么退款", "错误码 E1024 怎么处理"]:
        print(f"\n===== 问题：{query} =====")
        print_results("语义检索：", semantic_search(query))
        print_results("关键词检索：", keyword_search(query))


if __name__ == "__main__":
    main()
