"""RAG 文档摄取基础：读取、清洗、切块、生成 metadata。

本章离线运行，不调用模型 API。它演示 RAG 入库前最小的数据准备流程。

运行：
    uv run tutorials/07_rag/05_document_ingestion_basics/main.py
"""

from pathlib import Path


KNOWLEDGE_BASE = Path(__file__).parents[1] / "knowledge_base"


def clean_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        cleaned.append(line)
        previous_blank = blank
    return "\n".join(cleaned).strip()


def split_by_heading(text: str) -> list[tuple[str, str]]:
    """按 Markdown 二级标题粗略切块。返回 (section, chunk_text)。"""
    chunks: list[tuple[str, str]] = []
    current_title = "全文"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                chunks.append((current_title, "\n".join(current_lines).strip()))
            current_title = line.removeprefix("## ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append((current_title, "\n".join(current_lines).strip()))
    return [(title, body) for title, body in chunks if body]


def ingest_markdown_file(path: Path) -> list[dict]:
    document_id = path.stem
    text = clean_text(path.read_text(encoding="utf-8"))
    chunks = split_by_heading(text)

    records = []
    for index, (section, chunk_text) in enumerate(chunks, start=1):
        records.append(
            {
                "chunk_id": f"{document_id}:{index:04d}",
                "document_id": document_id,
                "source": str(path.relative_to(KNOWLEDGE_BASE.parent)),
                "section": section,
                "chunk_index": index,
                "text": chunk_text,
            }
        )
    return records


def main() -> None:
    all_chunks: list[dict] = []
    for path in sorted(KNOWLEDGE_BASE.glob("*.md")):
        chunks = ingest_markdown_file(path)
        all_chunks.extend(chunks)
        print(f"{path.name}: {len(chunks)} chunks")

    print(f"\n总 chunk 数：{len(all_chunks)}")
    print("\n示例 chunk metadata：")
    sample = all_chunks[0]
    for key in ["chunk_id", "document_id", "source", "section", "chunk_index"]:
        print(f"  {key}: {sample[key]}")
    print("\n示例 chunk 文本预览：")
    print(sample["text"][:300])


if __name__ == "__main__":
    main()
