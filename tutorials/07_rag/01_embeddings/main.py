"""文本向量（Embedding）与语义相似度：RAG 的地基。

演示：把若干句子转成向量，用余弦相似度衡量语义接近程度，
看看"语义搜索"如何在不懂关键词匹配的情况下找到相关句子。
"""

import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置：优先本章目录下的 .env（参考 .env.example），
# 其次从当前目录向上查找（如项目根目录）；已存在的环境变量不会被覆盖
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

# 读取 OPENAI_API_KEY；使用第三方兼容服务时同时设置 OPENAI_BASE_URL
client = OpenAI()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def get_embeddings(texts: list[str]) -> np.ndarray:
    """调用 Embedding 接口，把一批文本转成向量矩阵，shape = (len(texts), 维度)。"""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """计算一个查询向量与矩阵中每一行的余弦相似度，返回分数数组。

    余弦相似度衡量两个向量的方向是否一致（不看长度）：
        cos(θ) = (a · b) / (|a| × |b|)    取值 [-1, 1]，越接近 1 语义越相近
    若先把向量都缩放成单位向量（长度为 1），分母就是 1，公式退化为 a · b——
    归一化之后，点积就是余弦相似度。本函数正是利用这一点，用一次矩阵乘法
    代替逐个点积，几千个候选也能毫秒级算完（第 3 章 VectorStore 用的同一招）。
    """
    # 查询向量归一化：norm 算 L2 范数（长度），向量除以自身长度 -> 单位向量
    # 例：[3, 4] / 5 = [0.6, 0.8]，方向不变，长度变 1
    query = query / np.linalg.norm(query)

    # 矩阵逐行归一化：matrix 形状 (n, d)，即 n 个候选文本各 d 维
    # axis=1：对每一行单独算长度，得 n 个标量；
    # keepdims=True：保持二维形状 (n, 1)，除法才能广播——(n, d) / (n, 1) 表示每行除以它自己的长度
    matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)

    # @ 是矩阵乘法：(n, d) @ (d,) -> (n,)
    # 结果第 i 个元素 = 第 i 行 · query；此时向量都是单位向量，点积即余弦相似度
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
