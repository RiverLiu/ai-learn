# 06 Embeddings API

Chat API 让模型生成文本；Embeddings API 把文本变成向量。
向量可以用于语义相似度、搜索、聚类、推荐和 RAG。

## 本章要点

- Embedding 是文本的数值表示。
- 语义相近的文本，向量距离通常更近。
- RAG 的检索阶段依赖 embedding。
- 向量模型和聊天模型要分开配置。
- 批量 embedding、缓存和模型一致性非常重要。

## 最小调用

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

resp = client.embeddings.create(
    model=model,
    input="云雀笔记支持离线编辑和多端同步。",
)

vector = resp.data[0].embedding
print(len(vector))
print(vector[:5])
```

运行前确保 `.env` 中有：

```text
OPENAI_API_KEY=...
EMBEDDING_MODEL=text-embedding-3-small
```

如果使用 OpenAI 兼容服务，确认该服务真的提供 `/embeddings` 接口。

## 相似度计算

最常见的是余弦相似度：

```python
import numpy as np

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
```

示例：

```text
query = "会员能退款吗？"
doc1 = "购买后 7 天内可以申请退款。"
doc2 = "云雀笔记支持 Markdown 编辑。"
```

通常 `query` 与 `doc1` 的相似度会高于 `doc2`。

## 批量 Embedding

不要对每个 chunk 单独发一次请求。多数 API 支持批量输入：

```python
texts = [
    "专业版每月 29 元。",
    "购买后 7 天内可以申请退款。",
    "云雀笔记支持离线编辑。",
]

resp = client.embeddings.create(model=model, input=texts)
vectors = [item.embedding for item in resp.data]
```

批量处理的好处：

- 减少 HTTP 请求次数。
- 提高吞吐。
- 更容易做失败重试。

## 模型一致性

索引时和查询时必须使用同一个 embedding 模型。

```text
索引：text-embedding-3-small
查询：bge-m3
```

这种混用会导致向量空间不一致，检索结果不可信。

换 embedding 模型后必须重建索引。

## 缓存

Embedding 结果适合缓存，因为同一段文档反复 embedding 没有意义。

缓存 key 可以使用：

```text
embedding_model + sha256(text)
```

如果文档文本或 embedding 模型变化，就重新生成。

## 与 RAG 的关系

RAG 的离线索引：

```text
文档 → 切块 → Embedding → 存向量
```

RAG 的在线查询：

```text
用户问题 → Embedding → 向量相似度检索 → 相关 chunk
```

这就是为什么 RAG 模块会要求配置 `EMBEDDING_MODEL`。

## 常见错误

**服务没有 embeddings 接口。**

有些 OpenAI 兼容服务只提供聊天模型。报 404 或模型不存在时，先查平台是否支持 embedding。

**向量维度对不上。**

说明索引里混入了不同模型的向量。清空索引，用同一个模型重建。

**把长文档整体 embedding。**

长文档应先切块，否则向量会变得过于平均，检索粒度太粗。

## 练习

1. 选 3 句相似文本和 3 句不相似文本。
2. 调用 Embeddings API 得到向量。
3. 计算 query 与每个候选句的余弦相似度。
4. 观察排序是否符合直觉。

完成后继续学习 [RAG 第 1 章](../../07_rag/01_embeddings/)。
