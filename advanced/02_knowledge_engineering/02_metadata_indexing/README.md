# 02 元数据与索引设计

本章关注 chunk 旁边的“附属信息”：来源、版本、权限、时间、租户、文档类型和引用位置。

## 为什么元数据重要

没有元数据，RAG 只能回答“文本里有什么”；有了元数据，RAG 才能做到：

- 只检索当前用户有权限看的内容。
- 告诉用户答案来自哪个文档、章节和页码。
- 文档更新后禁用旧版本。
- 线上答错时定位到具体 chunk。

## 示例字段

```json
{
  "chunk_id": "pricing:v3:0012",
  "document_id": "pricing",
  "document_version": 3,
  "tenant_id": "acme",
  "permission_group": "support",
  "source_uri": "s3://kb/pricing.pdf",
  "section": "企业版",
  "page_start": 6,
  "page_end": 7,
  "document_status": "active",
  "updated_at": "2026-08-08T10:00:00+08:00"
}
```

## 练习

为 `tutorials/rag/knowledge_base` 中的三篇 Markdown 设计统一 metadata schema，并说明每个字段用于哪个生产问题。
