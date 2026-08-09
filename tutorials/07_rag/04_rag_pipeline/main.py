"""完整 RAG：检索 + 生成，让 LLM 基于知识库回答问题并附出处。

流程：构建内存索引（加载 → 切块 → 向量化）→ 对问题检索 Top-K 块
→ 把块拼入提示词 → LLM 生成回答 → 输出答案与来源。

运行：uv run tutorials/07_rag/04_rag_pipeline/main.py "你的问题"
"""

import os
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置：优先本章目录下的 .env，其次向上查找（如项目根目录）
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

KB_DIR = Path(__file__).parent.parent / "knowledge_base"

client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Embedding 接口批量向量化文本。"""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


def chunk_by_heading(text: str) -> list[str]:
    """按 Markdown 标题切块。"""
    chunks, current = [], ""
    for line in text.splitlines():
        if line.startswith("#") and current.strip():
            chunks.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def build_index(kb_dir: Path) -> tuple[list[dict], np.ndarray]:
    """加载知识库，切块并向量化，返回 (块列表, 归一化向量矩阵)。"""
    chunks = [
        {"source": path.name, "text": text}
        for path in sorted(kb_dir.glob("*.md"))
        for text in chunk_by_heading(path.read_text(encoding="utf-8"))
    ]
    vectors = get_embeddings([c["text"] for c in chunks])
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    return chunks, vectors


def retrieve(question: str, chunks: list[dict], vectors: np.ndarray, top_k: int = 3) -> list[dict]:
    """检索与问题最相关的 top_k 个块。"""
    query = get_embeddings([question])[0]
    query = query / np.linalg.norm(query)
    scores = vectors @ query
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [{"score": float(scores[i]), **chunks[i]} for i in top_indices]


def ask(question: str, contexts: list[dict]) -> str:
    """把检索到的上下文拼入提示词，让 LLM 基于它回答。"""
    context_text = "\n\n".join(
        f"【资料{i + 1}】（来源：{c['source']}）\n{c['text']}"
        for i, c in enumerate(contexts)
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是知识库问答助手。只根据给定的资料回答问题，"
                    "资料中没有的信息就明说不知道，不要编造。"
                    "回答结尾用【来源：xxx】注明依据的资料。"
                ),
            },
            {
                "role": "user",
                "content": f"资料：\n{context_text}\n\n问题：{question}",
            },
        ],
    )
    return response.choices[0].message.content


def main():
    question = " ".join(sys.argv[1:]) or "专业版多少钱？学生有优惠吗？"

    print("正在构建索引...")
    chunks, vectors = build_index(KB_DIR)

    contexts = retrieve(question, chunks, vectors)
    print(f"\n检索到 {len(contexts)} 个相关块：")
    for c in contexts:
        print(f"  {c['score']:.3f}  [{c['source']}] {c['text'].splitlines()[0]}")

    print(f"\n问题：{question}")
    print(f"回答：{ask(question, contexts)}")


if __name__ == "__main__":
    main()
