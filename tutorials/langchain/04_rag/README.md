# 04 用 LangChain 重写 RAG

本章把 [rag 教程](../../rag/)的手写流水线原样搬上 LangChain：**每一步对应一个框架组件**，
最后组装成一条 LCEL 链。学完可以对两版逐行对比，体会框架做了什么、没做什么。

## 手写版 vs LangChain 版

| 步骤 | 手写（rag 教程） | LangChain 组件 |
| --- | --- | --- |
| 加载 | `Path.read_text` | `Document`（生产中用 langchain-community 的 `DirectoryLoader`） |
| 切块 | 自写 `chunk_by_heading` | `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` |
| 向量化 | `client.embeddings.create` | `OpenAIEmbeddings` |
| 向量库 | 自写 `VectorStore` | `InMemoryVectorStore`（生产换 Chroma/Qdrant 等） |
| 检索 | `store.search()` | `retriever = vectorstore.as_retriever(k=3)` |
| 生成 | 拼字符串 + `chat.completions` | `{"context": retriever \| ..., "question": ...} \| prompt \| model` |

## 本章要点

- 文本被封装为 `Document`（`page_content` + `metadata`），来源文件名放进 `metadata["source"]`，
  供回答时标注出处；生产中可用 langchain-community 的 `DirectoryLoader` 加载更多格式。
- 两级切块：先按标题结构切，超长块再由 `RecursiveCharacterTextSplitter` 细分。
- 检索器直接接进 LCEL 链：dict 里 `context` 走检索分支，`question` 用 `RunnablePassthrough` 原样透传。

## 运行

需要模型 + Embeddings 接口（见[教程首页](../README.md#模型配置)；示例知识库为虚构产品"云雀笔记"文档）：

```bash
uv run tutorials/langchain/04_rag/main.py "专业版多少钱？学生有优惠吗？"
uv run tutorials/langchain/04_rag/main.py "离线编辑冲突了怎么办"
```

## 核心概念

- **框架的价值在替换成本**：想把内存向量库换成 Chroma，只改 `InMemoryVectorStore` 一行，
  链条其余部分不动——这是手写版做不到的。
- **原理没有变化**：检索质量仍然取决于切块与 Embedding，框架不解决原理问题，
  原理请回到 [rag 教程](../../rag/)。
