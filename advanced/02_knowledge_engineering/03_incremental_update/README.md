# 03 增量更新与删除

生产知识库不能每次都全量重建。文档新增、修改、删除、权限变化，都需要有明确策略。

## 推荐流程

```text
计算文档 hash
  ↓
hash 未变化：跳过
hash 变化：创建新版本
  ↓
解析、切块、embedding
  ↓
新 chunk 写入 active
  ↓
旧版本 chunk 标记 inactive
```

## 删除策略

删除文档时，不要只删数据库记录。还要：

- 删除或禁用向量库中的 chunk。
- 记录删除时间和操作人。
- 确保检索 filter 排除 deleted/inactive 文档。
- 必要时保留审计日志。

## 练习

设计一个 `documents` 表和一个 `chunks` 表，支持文档版本、删除和索引状态。
