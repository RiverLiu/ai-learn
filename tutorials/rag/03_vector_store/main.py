"""手写一个向量数据库：存储、检索、持久化。

向量数据库的核心就两件事：
1. 存：文本块 + 对应向量 + 元数据（来源）；
2. 取：给查询向量，返回余弦相似度最高的 Top-K 条。

本章用 numpy 实现一个最小可用版本，并用它给示例知识库构建索引、存到磁盘。
"""

import json
import os
from pathlib import Path

import numpy as np
from openai import OpenAI

KB_DIR = Path(__file__).parent.parent / "knowledge_base"
INDEX_PATH = Path(__file__).parent / "rag_index"  # 生成 rag_index.npz / rag_index.json

client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Embedding 接口批量向量化文本。"""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


class VectorStore:
    """最小向量库：内存检索 + 磁盘持久化。"""

    def __init__(self):
        self.vectors: np.ndarray | None = None  # shape = (块数, 维度)
        self.chunks: list[dict] = []            # [{"source": ..., "text": ...}]

    def add(self, chunks: list[dict], vectors: np.ndarray):
        """写入一批块及其向量（此处演示一次性构建，因此直接整体赋值）。"""
        self.chunks = chunks
        self.vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)  # 预先归一化

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> list[dict]:
        """返回与查询向量最相似的 top_k 个块，附带相似度分数。"""
        query_vector = query_vector / np.linalg.norm(query_vector)
        scores = self.vectors @ query_vector  # 归一化后点积 = 余弦相似度
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"score": float(scores[i]), **self.chunks[i]} for i in top_indices
        ]

    def save(self, path: Path):
        """向量存 .npz，文本与来源存 .json。"""
        np.savez(path.with_suffix(".npz"), vectors=self.vectors)
        path.with_suffix(".json").write_text(
            json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self, path: Path):
        self.vectors = np.load(path.with_suffix(".npz"))["vectors"]
        self.chunks = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))


def chunk_by_heading(text: str) -> list[str]:
    """按 Markdown 标题切块（与第 2 章相同的策略）。"""
    chunks, current = [], ""
    for line in text.splitlines():
        if line.startswith("#") and current.strip():
            chunks.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def build_index(kb_dir: Path) -> VectorStore:
    """离线索引构建全流程：加载文档 → 切块 → 向量化 → 写入向量库。"""
    chunks = [
        {"source": path.name, "text": text}
        for path in sorted(kb_dir.glob("*.md"))
        for text in chunk_by_heading(path.read_text(encoding="utf-8"))
    ]
    print(f"共切出 {len(chunks)} 个块，开始向量化...")
    vectors = get_embeddings([c["text"] for c in chunks])

    store = VectorStore()
    store.add(chunks, vectors)
    return store


def main():
    store = build_index(KB_DIR)
    store.save(INDEX_PATH)
    print(f"索引已保存：{INDEX_PATH.with_suffix('.npz')} / {INDEX_PATH.with_suffix('.json')}")

    # 模拟一次检索
    question = "退款政策是什么"
    query_vector = get_embeddings([question])[0]
    print(f"\n查询：{question}")
    for hit in store.search(query_vector, top_k=3):
        preview = hit["text"].replace("\n", " ")[:50]
        print(f"  {hit['score']:.3f}  [{hit['source']}] {preview}...")


if __name__ == "__main__":
    main()
