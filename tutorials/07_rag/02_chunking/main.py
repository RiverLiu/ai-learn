"""文档切块（Chunking）：把知识库文档切成适合检索的块。

演示两种策略：
1. 固定窗口：按字符数切，带重叠（简单但可能切断语义）；
2. 结构感知：按 Markdown 标题切（块内语义完整，推荐作为默认策略）。

本章不调用任何 API，直接运行即可。
"""

from pathlib import Path

KB_DIR = Path(__file__).parent.parent / "knowledge_base"


def load_documents(kb_dir: Path) -> list[dict]:
    """读取知识库中的所有 Markdown 文件，返回 [{source, text}, ...]。"""
    docs = []
    for path in sorted(kb_dir.glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def chunk_fixed(text: str, size: int = 120, overlap: int = 30) -> list[str]:
    """固定窗口切块：每块 size 字符，相邻块重叠 overlap 字符以防切断上下文。"""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks


def chunk_by_heading(text: str, max_size: int = 300) -> list[str]:
    """按 Markdown 标题切块：标题作为块的开头保留上下文；
    超过 max_size 的小节再按段落细分。"""
    chunks = []
    current = ""
    for line in text.splitlines():
        if line.startswith("#") and current.strip():
            chunks.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())

    # 过长的块按空行（段落边界）再细分
    result = []
    for chunk in chunks:
        if len(chunk) <= max_size:
            result.append(chunk)
        else:
            heading, _, body = chunk.partition("\n")
            paragraph = ""
            for para in body.split("\n\n"):
                if len(paragraph) + len(para) > max_size and paragraph:
                    result.append((heading + "\n" + paragraph).strip())
                    paragraph = ""
                paragraph += para + "\n\n"
            if paragraph.strip():
                result.append((heading + "\n" + paragraph).strip())
    return result


def show(name: str, chunks: list[dict]):
    print(f"\n=== {name}：共 {len(chunks)} 块 ===")
    for i, chunk in enumerate(chunks[:3]):
        preview = chunk["text"].replace("\n", " ")[:60]
        print(f"  [{i}] ({chunk['source']}, {len(chunk['text'])} 字符) {preview}...")
    if len(chunks) > 3:
        print(f"  ... 其余 {len(chunks) - 3} 块略")


def main():
    docs = load_documents(KB_DIR)
    print(f"加载了 {len(docs)} 篇文档：{[d['source'] for d in docs]}")

    fixed = [
        {"source": d["source"], "text": t} for d in docs for t in chunk_fixed(d["text"])
    ]
    structured = [
        {"source": d["source"], "text": t} for d in docs for t in chunk_by_heading(d["text"])
    ]
    show("固定窗口（120 字符 / 重叠 30）", fixed)
    show("按标题结构（上限 300 字符）", structured)


if __name__ == "__main__":
    main()
