# RAG（检索增强生成）知识库教程

RAG（Retrieval-Augmented Generation）是让 LLM 回答"它本来不知道"的问题的标准方案：
先从你的知识库中**检索**出相关内容，再把内容塞进提示词让 LLM 基于它**生成**回答。

## 为什么需要 RAG

LLM 的知识截止于训练数据，且无法访问你的私有文档。两种主流补救方式：

- **微调（Fine-tuning）**：把知识"烙"进模型权重，成本高、更新慢、可能遗忘。
- **RAG**：知识存在外部数据库，提问时现查现用，成本低、可随时更新、答案可附出处。

大多数知识库问答、客服机器人场景，RAG 是首选。

## RAG 的两条流水线

```
【离线：索引构建】                        【在线：查询问答】
                                       
文档 → 切块 → Embedding → 向量库         问题 → Embedding → 检索 Top-K 相关块
（chunking）（向量化）   （存储）                            ↓
                                              相关块 + 问题 → 拼提示词 → LLM → 回答（附出处）
```

核心概念：

- **Embedding（向量嵌入）**：把文本映射为高维向量，语义相近的文本向量距离也近。这是"语义搜索"的基础。
- **Chunking（切块）**：文档太长无法整体入库存储和检索，需要切成大小合适的块，块的质量直接决定检索质量。
- **向量数据库**：存储向量并支持"找最相似的 K 个"（近似最近邻搜索，ANN）。
- **检索增强**：把检索到的文本块作为上下文注入提示词，并要求 LLM 只基于这些内容回答，减少幻觉。

## 章节目录

1. [01_embeddings](./01_embeddings/)：文本向量与语义相似度——RAG 的地基
2. [02_chunking](./02_chunking/)：文档切块策略（固定窗口 vs 结构，感知）
3. [03_vector_store](./03_vector_store/)：手写一个向量数据库，构建知识库索引
4. [04_rag_pipeline](./04_rag_pipeline/)：完整 RAG——检索 + 生成，带出处引用
5. [05_document_ingestion_basics](./05_document_ingestion_basics/)：文档准备、清洗、metadata 与来源保留
6. [06_evaluation_metrics](./06_evaluation_metrics/)：RAG 评估指标——检索、生成、引用与线上质量
99. [99_intreview](./99_intreview/)：RAG 高频面试题与参考答案

示例知识库放在 [knowledge_base](./knowledge_base/)（一个虚构产品"云雀笔记"的文档），第 2～6 章共用。

## 环境准备

依赖已包含在项目根目录的 `pyproject.toml` 中（`openai`、`numpy`），执行：

```bash
uv sync
```

第 1、3、4 章需要调用 Embedding / Chat 接口，先配置密钥：

```bash
export OPENAI_API_KEY="sk-..."
# 使用兼容 OpenAI 协议的服务时追加：
export OPENAI_BASE_URL="https://..."
export MODEL_NAME="..."        # 聊天模型，默认 gpt-4o-mini
export EMBEDDING_MODEL="..."   # 向量模型，默认 text-embedding-3-small
```

第 2、6 章不调用任何 API，可以无密钥直接运行。

## 参考

- OpenAI Embeddings：https://platform.openai.com/docs/guides/embeddings
- 生产级向量数据库：[Chroma](https://www.trychroma.com/)、[Qdrant](https://qdrant.tech/)、[pgvector](https://github.com/pgvector/pgvector)、[Milvus](https://milvus.io/)

## 常见面试题

**Q1：RAG 的基本流程是什么？**

参考答案：离线构建索引：文档清洗、切块、embedding、入库；在线问答：问题 embedding、检索、拼上下文、生成答案。

**Q2：为什么需要切块？**

参考答案：文档太长不能整体检索或放入上下文。切块提高检索粒度，但过大有噪声，过小会丢上下文。

**Q3：Embedding 在 RAG 中的作用是什么？**

参考答案：Embedding 把文本映射成向量，使语义相近的问题和文档 chunk 在向量空间中更接近。

**Q4：为什么索引和查询必须使用同一个 embedding 模型？**

参考答案：不同 embedding 模型的向量空间不同，混用会导致相似度失真，换模型必须重建索引。

**Q5：Top-K 如何影响效果？**

参考答案：K 太小可能漏召回，K 太大可能引入噪声并增加成本。生产中常结合 rerank 和上下文压缩。

**Q6：RAG 能完全消除幻觉吗？**

参考答案：不能。检索失败、文档过期、排序错误或模型忽略证据时仍会幻觉，需要引用、拒答和评估。

**Q7：为什么 metadata 很重要？**

参考答案：metadata 支持来源引用、权限过滤、版本管理和问题定位。没有 metadata，答案即使正确也难以审计。

**Q8：向量库和普通数据库有什么区别？**

参考答案：向量库擅长相似度检索，普通数据库擅长结构化查询。生产 RAG 常同时使用两者。

**Q9：RAG 失败如何排查？**

参考答案：先看是否召回正确文档，再看排序、chunk 内容、上下文拼接和模型回答是否忠实。

**Q10：为什么文档更新后要重建索引？**

参考答案：文档内容变化会改变 chunk 和 embedding。旧向量不删除会导致模型回答过期信息。
