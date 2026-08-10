# 03 生产级 RAG 进阶

基础 RAG 的流程是：

```text
问题 -> 向量检索 -> 拼上下文 -> 生成答案
```

生产 RAG 不是把向量库换大一点，而是把“为什么答错”拆开定位：

- 相关资料没有被召回。
- 资料召回了，但排得太靠后。
- 上下文里有答案，但模型没有忠实使用证据。
- 检索到了用户不该看的资料。
- 文档版本过期，答案引用了旧政策。
- PDF、图片、表格、扫描件没有被正确解析成可检索证据。

本章改成一组离线可运行的小实验。每个实验只解决一个问题，先看失败输出，再加一个生产策略。

## 学习路径

建议按顺序学习：

1. [01_failure_diagnosis](./01_failure_diagnosis/)：先学会看 Top-K，判断 RAG 到底失败在哪一层。
2. [02_hybrid_search](./02_hybrid_search/)：理解为什么向量检索不擅长错误码、参数名、套餐名等精确词。
3. [03_rrf_merge](./03_rrf_merge/)：用 RRF 合并向量检索和关键词检索结果。
4. [04_rerank](./04_rerank/)：理解“多召回”和“精排序”为什么要分两阶段。
5. [05_metadata_filter_context](./05_metadata_filter_context/)：加入权限、版本过滤、上下文去重和引用编号。
6. [06_multimodal_retrieval](./06_multimodal_retrieval/)：处理 PDF、图片、OCR、Caption 和图文混合检索。

所有示例都不调用模型 API，可以直接运行：

```bash
uv run advanced/03_production_rag/01_failure_diagnosis/main.py
uv run advanced/03_production_rag/02_hybrid_search/main.py
uv run advanced/03_production_rag/03_rrf_merge/main.py
uv run advanced/03_production_rag/04_rerank/main.py
uv run advanced/03_production_rag/05_metadata_filter_context/main.py
uv run advanced/03_production_rag/06_multimodal_retrieval/main.py
```

## 生产 RAG 链路

学完小实验后，再回来看完整链路：

```text
用户问题
  ↓
意图识别 / 安全检查
  ↓
query rewrite / multi-query
  ↓
metadata filter
  ↓
向量检索 + 关键词检索
  ↓
RRF / 加权融合
  ↓
rerank
  ↓
上下文压缩 / 去重 / 引用整理
  ↓
生成答案
  ↓
忠实度检查 / 引用检查
```

每一层都要能单独观察。不要一看到答错就改 prompt。

## 核心概念速记

| 概念 | 解决的问题 | 常见误区 |
| --- | --- | --- |
| Query rewrite | 用户问法太短、指代不清、口语化 | 过度改写，丢掉错误码和专有名词 |
| Hybrid search | 语义相似和精确关键词各有短板 | 以为混合检索等于简单拼接两个列表 |
| RRF | 多路召回结果融合 | 只看分数，不看排名来源 |
| Rerank | 候选很多时重新精排 | 直接用 rerank 替代召回 |
| Metadata filter | 权限、租户、版本、语言过滤 | 依赖 prompt 约束模型不要看敏感资料 |
| Context packing | 控制进入 LLM 的证据质量 | 把 Top-K 全部无脑拼进 prompt |
| OCR / Caption | 把图片、扫描 PDF、图表转成文本证据 | 只做 OCR，不保留页码、区域、图片位置 |
| Multimodal embedding | 图文映射到统一向量空间 | 不做领域评估就默认图文互搜可靠 |

## RAG 失败分类

| 类型 | 表现 | 先看什么 | 主要修复方向 |
| --- | --- | --- | --- |
| 无召回 | Top-K 没有正确资料 | Top-K 明细、Recall@K | 切块、embedding、query rewrite、hybrid |
| 召回有但排序低 | 正确 chunk 在后面 | MRR、nDCG、排名位置 | RRF、rerank、调 top_k |
| 上下文有但回答错 | 证据在 prompt 中但答案错 | prompt、答案事实、引用 | 引用约束、忠实度检查、评估样本 |
| 上下文过长 | 答案混乱、成本高 | token、重复 chunk、来源数量 | 去重、压缩、父子 chunk |
| 权限错误 | 检索到不该看的内容 | metadata、租户、权限组 | metadata filter、租户隔离 |
| 信息过期 | 回答旧政策 | updated_at、version、active | 版本过滤、增量更新 |
| 图文丢失 | PDF/图片里的答案找不到 | 解析结果、OCR、caption、页码 | 版面分析、OCR、caption、多模态检索 |

## 实践任务

完成本章后，把这些能力逐步迁移到 [tutorials/07_rag/04_rag_pipeline](../../tutorials/07_rag/04_rag_pipeline/)：

1. 给 chunk 添加 `document_type`、`permission_group`、`updated_at`。
2. 加入关键词检索。
3. 用 RRF 合并向量和关键词结果。
4. 先召回更多候选，再 rerank 到更少上下文。
5. 在检索前执行 metadata filter。
6. 为 PDF 页面、图片 OCR、图表 caption 设计统一 metadata。
