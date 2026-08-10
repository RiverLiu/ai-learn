"""Metadata filter and context packing demo.

Run:
    uv run advanced/03_production_rag/05_metadata_filter_context/main.py
"""

from __future__ import annotations


CURRENT_USER = {
    "tenant_id": "tenant_a",
    "groups": {"employee", "admin"},
}

RETRIEVED = [
    {
        "chunk_id": "pricing:enterprise:old",
        "document_id": "pricing",
        "source": "pricing.md",
        "text": "旧政策：团队版也支持 SSO。",
        "tenant_id": "tenant_a",
        "permission_group": "employee",
        "document_status": "archived",
        "updated_at": "2025-12-01",
    },
    {
        "chunk_id": "pricing:enterprise:new",
        "document_id": "pricing",
        "source": "pricing.md",
        "text": "企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。",
        "tenant_id": "tenant_a",
        "permission_group": "employee",
        "document_status": "active",
        "updated_at": "2026-07-01",
    },
    {
        "chunk_id": "internal:roadmap",
        "document_id": "roadmap",
        "source": "roadmap.md",
        "text": "内部路线图：未来可能给团队版增加 SSO。",
        "tenant_id": "tenant_a",
        "permission_group": "executive",
        "document_status": "active",
        "updated_at": "2026-08-01",
    },
    {
        "chunk_id": "other-tenant:pricing",
        "document_id": "pricing",
        "source": "pricing.md",
        "text": "其他租户的定制合同：团队版包含 SSO。",
        "tenant_id": "tenant_b",
        "permission_group": "employee",
        "document_status": "active",
        "updated_at": "2026-07-15",
    },
]


def allowed(chunk: dict) -> bool:
    return (
        chunk["tenant_id"] == CURRENT_USER["tenant_id"]
        and chunk["permission_group"] in CURRENT_USER["groups"]
        and chunk["document_status"] == "active"
    )


def pack_context(chunks: list[dict]) -> str:
    lines = []
    seen_text: set[str] = set()
    for index, chunk in enumerate(chunks, start=1):
        if chunk["text"] in seen_text:
            continue
        seen_text.add(chunk["text"])
        lines.append(
            f"[S{index} source={chunk['source']} doc={chunk['document_id']} updated={chunk['updated_at']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(lines)


def main() -> None:
    print("未过滤候选：")
    for item in RETRIEVED:
        print(
            f"- {item['chunk_id']} tenant={item['tenant_id']} group={item['permission_group']} "
            f"status={item['document_status']} updated={item['updated_at']}"
        )

    filtered = [item for item in RETRIEVED if allowed(item)]

    print("\nmetadata filter 后：")
    for item in filtered:
        print(f"- {item['chunk_id']} | {item['text']}")

    print("\n组装后的上下文：")
    print(pack_context(filtered))


if __name__ == "__main__":
    main()
