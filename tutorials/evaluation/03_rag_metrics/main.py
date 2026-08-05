"""检索质量评估：RAG 答非所问，多半是检索就没命中——先给"上半场"打分。

手写 numpy 余弦检索（与 rag 教程同款，不依赖 langchain），对知识库切块建索引，
用一份"问题 → 应命中文档 + 金句"的评估集计算 Top-3 命中率（Hit Rate@3），
再对比三种切块配置（固定窗口 200 字符 / 500 字符 / 按标题结构）的命中率——
用数据选参数，而不是拍脑袋。

命中判定分两级（运行后会发现区分度天差地别）：
- 文档级：Top-3 结果中包含目标文档即算命中——宽松，小知识库上容易"满分失真"；
- 金句级：Top-3 结果中有块包含回答问题所需的关键原文（gold）才算命中——严格、可区分。

运行：uv run tutorials/evaluation/03_rag_metrics/main.py
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置：优先本章目录下的 .env，其次向上查找（如项目根目录）
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

CHAPTER_DIR = Path(__file__).parent
EVAL_FILE = CHAPTER_DIR / "data" / "retrieval_eval.jsonl"
KB_DIR = CHAPTER_DIR.parent.parent / "rag" / "knowledge_base"  # 复用 rag 教程的知识库

client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
TOP_K = 3


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Embedding 接口批量向量化，并把每个向量归一化为单位向量。

    归一化之后，点积就是余弦相似度，检索时一次矩阵乘法即可算完。
    """
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    vectors = np.array([item.embedding for item in response.data])
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def chunk_fixed(text: str, size: int, overlap: int) -> list[str]:
    """固定窗口切块：每 size 字符一刀，相邻块重叠 overlap 字符防止答案被切断。"""
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + size].strip())
        start += size - overlap
    return [c for c in chunks if c]


def chunk_by_heading(text: str) -> list[str]:
    """结构感知切块：按 Markdown 标题切，每个块是一个语义完整的小节。"""
    chunks, current = [], ""
    for line in text.splitlines():
        if line.startswith("#") and current.strip():
            chunks.append(current.strip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def build_chunks(kb_dir: Path, chunk_fn) -> list[dict]:
    """加载知识库并用指定策略切块，每个块记录来源文档名。"""
    return [
        {"source": path.name, "text": text}
        for path in sorted(kb_dir.glob("*.md"))
        for text in chunk_fn(path.read_text(encoding="utf-8"))
    ]


def normalize(text: str) -> str:
    """去掉所有空白字符，避免"每月 9 元"与"每月9元"的写法差异影响包含判定。"""
    return "".join(text.split())


def evaluate(chunks: list[dict], chunk_vectors: np.ndarray,
             query_vectors: np.ndarray, items: list[dict], top_k: int) -> list[dict]:
    """逐问题检索 Top-K 并做命中判定，返回 [{doc_hit, gold_rank}]。

    gold_rank：包含金句的块在 Top-K 中的名次（1 最靠前），未命中为 0。
    名次比"是否命中"更细：Top-3 全命中时，名次仍能分出切块配置的高下。
    """
    results = []
    for query, item in zip(query_vectors, items):
        scores = chunk_vectors @ query  # 单位向量点积 = 余弦相似度
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_chunks = [chunks[i] for i in top_indices]
        gold_rank = 0
        for rank, c in enumerate(top_chunks, start=1):
            if normalize(item["gold"]) in normalize(c["text"]):
                gold_rank = rank
                break
        results.append({
            # 文档级：目标文档出现在 Top-K 中
            "doc_hit": any(c["source"] == item["source"] for c in top_chunks),
            "gold_rank": gold_rank,
        })
    return results


def main():
    with open(EVAL_FILE, encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]
    print(f"已加载检索评估集：{len(items)} 条；Embedding 模型：{EMBEDDING_MODEL}\n")

    # 三种切块配置同台对比：固定窗口 200 / 500 字符（重叠 20%）、按标题结构切块
    configs = [
        ("固定窗口200字符", lambda t: chunk_fixed(t, size=200, overlap=40)),
        ("固定窗口500字符", lambda t: chunk_fixed(t, size=500, overlap=100)),
        ("按标题结构切块", chunk_by_heading),
    ]

    print("正在向量化评估问题...")
    query_vectors = get_embeddings([item["question"] for item in items])

    all_results: dict[str, list[dict]] = {}
    for name, chunk_fn in configs:
        chunks = build_chunks(KB_DIR, chunk_fn)
        print(f"正在构建索引 [{name}]：{len(chunks)} 个块...")
        chunk_vectors = get_embeddings([c["text"] for c in chunks])
        all_results[name] = evaluate(chunks, chunk_vectors, query_vectors, items, TOP_K)

    # 逐问题命中明细：行=问题，列=切块配置，单元格=金句所在块的名次（✗=未进 Top-K）
    names = [name for name, _ in configs]
    print(f"\n===== 逐问题命中情况（Top-{TOP_K}，数字=金句块名次） =====")
    header = f"{'问题':<24}" + "".join(f"{name:<16}" for name in names)
    print(header)
    print("-" * len(header))
    for i, item in enumerate(items):
        question = item["question"][:22]
        marks = "".join(
            f"{all_results[n][i]['gold_rank'] or '✗':<16}" for n in names
        )
        print(f"{question:<24}{marks}  金句：{item['gold']}")

    print(f"\n===== 命中率对比（金句级判定） =====")
    print(f"{'配置':<14}{'文档级@' + str(TOP_K):<14}{'金句级@1':<14}{'金句级@' + str(TOP_K):<14}")
    for name in names:
        results = all_results[name]
        n = len(results)
        doc_hits = sum(r["doc_hit"] for r in results)
        gold_at_1 = sum(r["gold_rank"] == 1 for r in results)
        gold_at_k = sum(r["gold_rank"] > 0 for r in results)
        print(f"{name:<14}{doc_hits}/{n} = {doc_hits / n:.0%}"
              f"      {gold_at_1}/{n} = {gold_at_1 / n:.0%}"
              f"      {gold_at_k}/{n} = {gold_at_k / n:.0%}")


if __name__ == "__main__":
    main()
