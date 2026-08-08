# 02 知识工程

知识工程关注的是：如何把原始文件、网页、表格和业务资料变成可治理、可更新、可检索、可引用的知识库。

它是生产 RAG 的前置能力。如果数据进入知识库时就丢了结构、权限、版本和来源，后面的 rerank、prompt 和评估都只能补救一部分问题。

## 章节目录

1. [01_document_ingestion](./01_document_ingestion/)：文档解析、清洗、切块、元数据和增量索引
2. [02_metadata_indexing](./02_metadata_indexing/)：元数据设计、权限过滤、版本管理和引用展示
3. [03_incremental_update](./03_incremental_update/)：文档更新、删除、重建索引和幂等任务

## 学习目标

- 能说明文档摄取链路中的每个阶段。
- 能设计 chunk 的元数据字段。
- 能解释为什么权限过滤必须发生在检索前。
- 能设计文档增量更新和删除策略。

## 与基础教程的关系

先学 [tutorials/rag](../../tutorials/rag/) 理解 embedding、chunking 和向量检索。
再学本模块，把“手写知识库 demo”升级成“可维护知识库系统”。
