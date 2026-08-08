# 03 生产级 RAG 进阶

基础 RAG 的流程是“问题 → 向量检索 → 拼上下文 → 生成答案”。
生产 RAG 需要处理更复杂的问题：用户问法模糊、关键词精确匹配、权限过滤、召回不足、排序错误、引用不可信和答案幻觉。

## 本章要点

- 生产 RAG 是一组策略组合，不是单一向量库。
- 检索质量要拆成召回、排序、上下文组装和生成忠实度分别优化。
- hybrid search、rerank、query rewrite 和 metadata filter 是最常用的四个增强点。
- RAG 失败要能分类，否则只能靠感觉调参数。

## 生产 RAG 链路

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
结果合并
  ↓
rerank
  ↓
上下文压缩 / 去重 / 引用整理
  ↓
生成答案
  ↓
忠实度检查 / 引用检查
```

## Hybrid Search

向量检索擅长语义相似，关键词检索擅长精确命中。

| 问题类型 | 向量检索 | 关键词检索 |
| --- | --- | --- |
| “怎么退款” | 强 | 中 |
| “错误码 E1024” | 弱 | 强 |
| “S3UploadTimeout 参数” | 弱 | 强 |
| “会员到期后还能用吗” | 强 | 中 |

生产中常用混合方案：

```text
vector_results = vector_search(query, top_k=20)
keyword_results = bm25_search(query, top_k=20)
merged = reciprocal_rank_fusion(vector_results, keyword_results)
reranked = rerank(query, merged, top_k=5)
```

## Rerank

第一阶段检索负责“多召回”，rerank 负责“精排序”。

适合 rerank 的场景：

- top_k 很大，直接拼上下文成本高。
- 向量检索召回了相似但不回答问题的 chunk。
- 用户问题包含多个条件。
- 需要从多个文档里选最相关的少数段落。

常见 rerank 模型：

- 商业 rerank API
- bge-reranker 系列
- cross-encoder 模型
- 使用 LLM 做小规模重排

注意：LLM rerank 成本高、延迟大，适合低频高价值任务。

## Query Rewrite

用户问题常常不是适合检索的形式：

```text
用户：它到期后还能继续用吗？
改写：云雀笔记会员订阅到期后功能限制和数据保留规则是什么？
```

改写策略：

- 利用会话历史补全指代。
- 把口语问题改成检索关键词。
- 生成多个角度的问题。
- 保留专有名词和错误码，不要过度改写。

风险：

- 改写引入不存在的假设。
- 多轮对话中错解“它”指代。
- 把用户问题变窄，漏掉相关文档。

## Metadata Filter

metadata filter 是生产 RAG 的安全基础。

常见过滤字段：

- `tenant_id`
- `permission_group`
- `document_type`
- `product`
- `locale`
- `version`
- `updated_at`

示例：

```python
filters = {
    "tenant_id": current_user.tenant_id,
    "permission_group": {"$in": current_user.groups},
    "document_status": "active",
}
```

不要依赖 prompt 告诉模型“不要看别人的数据”。权限必须在检索前完成。

## 上下文组装

检索到 chunk 后，不应该直接全部拼进去。需要处理：

- 去重：同一文档相邻 chunk 是否合并。
- 截断：优先保留高相关、高权威、更新时间新的内容。
- 分组：按文档或主题组织上下文。
- 引用编号：给每段上下文稳定编号。
- 冲突：旧文档和新文档矛盾时提示模型优先级。

推荐上下文格式：

```text
[source: pricing.md#enterprise page=3 updated=2026-07-01]
企业版支持按年订阅...

[source: faq.md#refund page=8 updated=2026-06-15]
退款申请需在购买后 7 天内提交...
```

## RAG 失败分类

| 类型 | 表现 | 主要修复方向 |
| --- | --- | --- |
| 无召回 | 相关文档没被检索到 | 切块、embedding、query rewrite、hybrid |
| 召回有但排序低 | 相关 chunk 在 top_k 之外 | rerank、RRF、调 top_k |
| 上下文有但回答错 | 模型没遵守证据 | prompt、引用约束、忠实度检查 |
| 上下文过长 | 答案混乱或成本高 | 压缩、去重、父子 chunk |
| 权限错误 | 检索到不该看的内容 | metadata filter、租户隔离 |
| 信息过期 | 回答旧政策 | 文档版本、active 标记、增量更新 |

## 评估指标

检索指标：

- Recall@K
- MRR
- NDCG
- 命中文档率
- 命中 chunk 率

生成指标：

- answer correctness
- faithfulness
- citation precision
- citation recall
- refusal accuracy

线上指标：

- 用户追问率
- 点踩率
- 引用点击率
- “没有解决”反馈率
- 平均 token 成本

## 具体示例：一次 RAG 失败如何定位

用户问题：

```text
企业版支持 SSO 吗？
```

线上回答：

```text
支持，所有版本都支持 SSO。
```

人工检查发现正确答案是：

```text
只有企业版支持 SSO，团队版和个人版不支持。
```

不要直接改 prompt，先看链路。

### 第 1 步：看检索结果

```text
top1 faq.md#登录问题 score=0.82
top2 pricing.md#企业版能力 score=0.77
top3 product_intro.md#安全能力 score=0.73
```

`pricing.md#企业版能力` 命中了，但排在第二。问题不是“无召回”，而是排序和上下文组装可能有问题。

### 第 2 步：看上下文

```text
[faq.md#登录问题]
云雀笔记支持手机号、邮箱和第三方账号登录。

[pricing.md#企业版能力]
企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。
```

上下文里有正确答案，但模型答错，属于“上下文有但回答错”。

### 第 3 步：修复策略

Prompt 增加约束：

```text
如果不同版本、套餐、权限存在差异，必须逐项说明差异，不要把某个版本的能力推广到所有版本。
```

同时增加评估样本：

```json
{
  "input": "企业版支持 SSO 吗？",
  "expected_facts": ["企业版支持 SSO", "个人版和团队版不包含 SSO"],
  "forbidden_facts": ["所有版本都支持 SSO"]
}
```

这个例子说明：RAG 优化要先分类失败，再决定改切块、检索、rerank、prompt 还是数据。

## 实践任务

在 [tutorials/rag/04_rag_pipeline](../../tutorials/rag/04_rag_pipeline/) 基础上升级：

1. 加入关键词检索。
2. 用 RRF 合并向量和关键词结果。
3. 为每个 chunk 添加 `document_type` 和 `updated_at`。
4. 实现 metadata filter。
5. 给评估集增加“错误码”“套餐名”“退款规则”等精确查询。
