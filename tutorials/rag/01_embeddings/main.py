"""文本向量（Embedding）与语义相似度：RAG 的地基。

演示：把若干句子转成向量，用余弦相似度衡量语义接近程度，
看看"语义搜索"如何在不懂关键词匹配的情况下找到相关句子。
"""

import os

import numpy as np
from openai import OpenAI

# 读取 OPENAI_API_KEY；使用第三方兼容服务时同时设置 OPENAI_BASE_URL
client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Embedding 接口，把一批文本转成向量矩阵，shape = (len(texts), 维度)。"""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """计算一个查询向量与矩阵中每一行的余弦相似度，返回分数数组。"""
    query = query / np.linalg.norm(query)
    matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix @ query


def main():
    candidates = [
        "专业版每月 18 元，按年付费有优惠",      # 相关：价格
        "团队版支持 SSO 单点登录",
        "云雀笔记专业版的定价是多少？",            # 相关：与问题同义不同字
        "离线模式下修改会自动合并",
        "React 是一个用于构建用户界面的 JavaScript 库",  # 无关
    ]
    query = "专业版多少钱"

    # 把查询和所有候选句一起向量化，第 0 条是查询
    vectors = get_embeddings([query] + candidates)
    scores = cosine_similarity(vectors[0], vectors[1:])

    print(f"查询：{query}\n")
    for score, text in sorted(zip(scores, candidates), reverse=True):
        print(f"  {score:.3f}  {text}")


if __name__ == "__main__":
    main()
