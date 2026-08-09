"""本地向量模型：用 Ollama 上的 bge-m3 生成 Embedding，复现 RAG 第 1 章的语义排序演示。

与 tutorials/07_rag/01_embeddings/main.py 做的是同一个实验（查询 + 候选句、余弦相似度排序），
区别只在于向量模型从 OpenAI 的 text-embedding-3-small 换成本机的 bge-m3——
代码骨架不变，因为 Ollama 的 /v1 端点与 OpenAI 协议兼容。

脚本采用"检测-引导"模式，保证任何时候都能运行：
- Ollama 在线且已拉取 bge-m3：真实生成向量并排序；
- 否则：打印安装与配置指引，正常退出（退出码 0）。
"""

import httpx
import numpy as np

# 与上一章相同的探测方式：Ollama 原生接口 /api/tags 列出本机已安装模型
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
EMBEDDING_MODEL = "bge-m3"  # 智源 BAAI 的开源向量模型，1024 维，中文效果好


def list_local_models() -> list[str] | None:
    """探测 Ollama 服务：在线返回已安装模型名列表，不在线返回 None（2 秒超时，不抛异常）。"""
    try:
        resp = httpx.get(OLLAMA_TAGS_URL, timeout=2.0)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except httpx.HTTPError:
        return None


def print_install_guide():
    """本机没有 Ollama（或没拉 bge-m3）时：打印指引（随后正常退出）。"""
    print("未检测到可用的本地向量模型。按下面步骤准备后重跑本脚本：\n")
    print("【第 1 步】安装 Ollama（如已按第 1 章装好可跳过）")
    print("  macOS   : https://ollama.com/download/mac 下载安装并启动；或 brew install --cask ollama")
    print("  Linux   : curl -fsSL https://ollama.com/install.sh | sh")
    print("  Windows : https://ollama.com/download/windows 下载 OllamaSetup.exe 安装\n")
    print("【第 2 步】拉取向量模型 bge-m3（约 1 GB 出头）")
    print(f"  ollama pull {EMBEDDING_MODEL}")
    print("  注意：bge-m3 是纯向量模型，ollama run 它会报 does not support generate，属正常现象。\n")
    print("【第 3 步】让 RAG 教程也用上它：在项目根目录 .env 中（沿用第 1 章的聊天配置）追加")
    print(f"  EMBEDDING_MODEL={EMBEDDING_MODEL}\n")
    print("【提醒】换 Embedding 模型后必须重建 RAG 索引（维度与语义空间都变了）：")
    print("  rm -f tutorials/07_rag/03_vector_store/rag_index.npz tutorials/07_rag/03_vector_store/rag_index.json")
    print("  uv run tutorials/07_rag/03_vector_store/main.py")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Ollama 的 OpenAI 兼容端点，把一批文本转成向量矩阵，shape = (len(texts), 维度)。"""
    from openai import OpenAI

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """计算查询向量与矩阵每行的余弦相似度（与 rag/01_embeddings 相同的写法）。

    先把所有向量归一化成单位向量，之后点积就等于余弦相似度，
    用一次矩阵乘法代替逐个点积，取值 [-1, 1]，越接近 1 语义越相近。
    """
    query = query / np.linalg.norm(query)
    matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix @ query


def main():
    models = list_local_models()
    if models is None:
        print_install_guide()
        return  # 正常退出，退出码 0

    if not any(m == EMBEDDING_MODEL or m.startswith(f"{EMBEDDING_MODEL}:") for m in models):
        print(f"Ollama 服务在线，但还没拉取 {EMBEDDING_MODEL}。先执行：ollama pull {EMBEDDING_MODEL}")
        return

    print(f"检测到 Ollama 在线，使用本地向量模型 {EMBEDDING_MODEL}（全程离线，不发网络请求）\n")

    # 与 rag/01_embeddings 同款的"查询 + 候选句"：两条价格相关应排前，React 条目应垫底
    candidates = [
        "专业版每月 18 元，按年付费有优惠",          # 相关：价格
        "云雀笔记专业版的定价是多少？",                # 相关：与查询同义不同字
        "React 是一个用于构建用户界面的 JavaScript 库",  # 无关
    ]
    query = "专业版多少钱"

    # 第 0 条是查询，其余是候选；bge-m3 输出 1024 维向量
    vectors = get_embeddings([query] + candidates)
    print(f"向量维度：{vectors.shape[1]}（换模型后维度会变，RAG 索引必须重建）\n")

    scores = cosine_similarity(vectors[0], vectors[1:])
    print(f"查询：{query}\n")
    for score, text in sorted(zip(scores, candidates), reverse=True):
        print(f"  {score:.3f}  {text}")


if __name__ == "__main__":
    main()
