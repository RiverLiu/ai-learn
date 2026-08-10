"""Multimodal retrieval demo.

This script simulates evidence extracted from PDF pages, images, OCR, and
captions. It does not call OCR or vision models; the goal is to show how the
retrieval records should be structured and selected.

Run:
    uv run advanced/03_production_rag/06_multimodal_retrieval/main.py
"""

from __future__ import annotations

import re


EVIDENCE = [
    {
        "chunk_id": "policy-refund:page-2:text",
        "source": "policy-refund.pdf",
        "modality": "pdf_text",
        "page": 2,
        "region": "full-page",
        "text": "退款申请需在购买后 7 天内提交，超过 7 天不支持原路退款。",
        "image_ref": "s3://kb/policy-refund/page-2.png",
        "confidence": 1.0,
    },
    {
        "chunk_id": "invoice-2026-001:page-1:ocr",
        "source": "invoice-2026-001.pdf",
        "modality": "ocr_text",
        "page": 1,
        "region": "x=80,y=120,w=600,h=180",
        "text": "发票金额 1280 元，购买方：云雀科技，开票日期：2026-07-18。",
        "image_ref": "s3://kb/invoice-2026-001/page-1.png",
        "confidence": 0.93,
    },
    {
        "chunk_id": "screenshot-e1024:caption",
        "source": "support-ticket-8848.png",
        "modality": "image_caption",
        "page": None,
        "region": "full-image",
        "text": "产品上传页面弹出错误码 E1024，提示文件超过大小限制，页面右下角有重试按钮。",
        "image_ref": "s3://kb/support-ticket-8848.png",
        "confidence": 0.88,
    },
    {
        "chunk_id": "report-q2:page-6:chart-caption",
        "source": "report-q2.pdf",
        "modality": "chart_caption",
        "page": 6,
        "region": "x=60,y=210,w=720,h=360",
        "text": "柱状图显示 2026 年 Q2 企业版收入高于团队版和个人版，企业版为 320 万元。",
        "image_ref": "s3://kb/report-q2/page-6.png",
        "confidence": 0.86,
    },
]

DOMAIN_TERMS = [
    "发票",
    "金额",
    "发票金额",
    "E1024",
    "截图",
    "错误码",
    "Q2",
    "企业版",
    "收入",
    "柱状图",
    "退款",
]


QUERY_INTENTS = {
    "发票金额是多少": {"ocr_text", "pdf_text"},
    "截图里的 E1024 是什么问题": {"image_caption", "ocr_text"},
    "Q2 企业版收入是多少": {"chart_caption", "pdf_text"},
}


def tokenize(text: str) -> set[str]:
    lowered = text.lower()
    tokens = set(re.findall(r"[a-z0-9_]+", lowered))
    for term in DOMAIN_TERMS:
        if term.lower() in lowered:
            tokens.add(term.lower())
    return tokens


def retrieve(query: str, top_k: int = 3) -> list[tuple[dict, float]]:
    query_terms = tokenize(query)
    preferred_modalities = QUERY_INTENTS.get(query, {"pdf_text", "ocr_text", "image_caption", "chart_caption"})
    scored = []
    for item in EVIDENCE:
        text_terms = tokenize(item["text"])
        keyword_score = len(query_terms & text_terms)
        modality_bonus = 2 if item["modality"] in preferred_modalities else 0
        confidence_bonus = item["confidence"]
        score = keyword_score + modality_bonus + confidence_bonus
        scored.append((item, score))
    return sorted(scored, key=lambda pair: pair[1], reverse=True)[:top_k]


def print_results(query: str) -> None:
    print(f"\n===== 问题：{query} =====")
    for rank, (item, score) in enumerate(retrieve(query), start=1):
        page = f"page={item['page']}" if item["page"] is not None else "page=n/a"
        print(
            f"{rank}. {item['chunk_id']} score={score:.2f} "
            f"modality={item['modality']} {page} confidence={item['confidence']}"
        )
        print(f"   text: {item['text']}")
        print(f"   evidence: {item['source']} {item['region']} {item['image_ref']}")


def main() -> None:
    for query in ["发票金额是多少", "截图里的 E1024 是什么问题", "Q2 企业版收入是多少"]:
        print_results(query)


if __name__ == "__main__":
    main()
