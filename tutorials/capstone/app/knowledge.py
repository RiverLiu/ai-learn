"""知识库：加载文档、按标题切块、构建内存向量索引、余弦相似度检索。

与 rag 教程 04_rag_pipeline 同一套路：numpy 手写向量检索，
不引入额外向量数据库——索引就在进程内存里，随服务启动构建一次。
"""

from pathlib import Path

import numpy as np
from openai import OpenAI

from .config import load_embedding_config

KB_DIR = Path(__file__).parent.parent / "data" / "knowledge_base"


def chunk_by_heading(text: str) -> list[str]:
    """按 Markdown 标题切块：每个标题段落是一个块。"""
    chunks, current = [], ""
    for line in text.splitlines():
        if line.startswith("#") and current.strip():
            chunks.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


class KnowledgeBase:
    """内存向量索引：块列表 + 归一化向量矩阵，余弦相似度取 Top-K。"""

    def __init__(self, kb_dir: Path = KB_DIR):
        config = load_embedding_config()
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self._model = config.model
        self.chunks: list[dict] = []
        self.vectors: np.ndarray | None = None
        self._build(kb_dir)

    def _embed(self, texts: list[str]) -> np.ndarray:
        """调用 Embedding 接口批量向量化文本。"""
        response = self._client.embeddings.create(model=self._model, input=texts)
        return np.array([item.embedding for item in response.data])

    def _build(self, kb_dir: Path) -> None:
        chunks = [
            {"source": path.name, "text": text}
            for path in sorted(kb_dir.glob("*.md"))
            for text in chunk_by_heading(path.read_text(encoding="utf-8"))
        ]
        if not chunks:
            raise RuntimeError(f"知识库为空：{kb_dir} 下没有 .md 文档")
        vectors = self._embed([c["text"] for c in chunks])
        self.chunks = chunks
        self.vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """检索与问题最相关的 top_k 个块，返回带相似度分数和来源的段落。"""
        query_vec = self._embed([query])[0]
        query_vec = query_vec / np.linalg.norm(query_vec)
        scores = self.vectors @ query_vec
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [{"score": float(scores[i]), **self.chunks[i]} for i in top_indices]
