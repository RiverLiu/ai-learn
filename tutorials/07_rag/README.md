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

示例知识库放在 [knowledge_base](./knowledge_base/)（一个虚构产品"云雀笔记"的文档），第 2～5 章共用。

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

第 2 章不调用任何 API，可以无密钥直接运行。

## 参考

- OpenAI Embeddings：https://platform.openai.com/docs/guides/embeddings
- 生产级向量数据库：[Chroma](https://www.trychroma.com/)、[Qdrant](https://qdrant.tech/)、[pgvector](https://github.com/pgvector/pgvector)、[Milvus](https://milvus.io/)
