# 03 RRF 结果融合

Hybrid Search 会产生两组结果：向量检索结果和关键词检索结果。下一步要把它们合成一个候选列表。

RRF（Reciprocal Rank Fusion）是一种常见融合方法。它不依赖不同检索器的原始分数是否可比，只使用排名：

```text
score = 1 / (k + rank)
```

这里：

- `rank` 表示某个 chunk 在某一路检索结果里的排名，从 `1` 开始。排第 1 就是 `rank=1`，排第 3 就是 `rank=3`。
- `k` 是 RRF 的平滑常数，用来控制排名差距对分数的影响。常见默认值是 `60`。`k` 越大，不同排名之间的分数差距越小；`k` 越小，靠前排名的优势越明显。

如果同一个 chunk 同时出现在多路检索结果里，它的分数会累加。例如某个 chunk 在向量检索排第 2，在关键词检索排第 1：

```text
score = 1 / (60 + 2) + 1 / (60 + 1)
```

同一个 chunk 如果在多路检索中都靠前，融合后会更靠前。

## 为什么需要 RRF

向量检索和关键词检索的原始分数通常不是一个量纲：

```text
向量相似度：0.82
BM25 分数：13.7
```

这两个数字不能直接相加，也不能直接比较大小。`13.7` 并不一定比 `0.82` 更相关，它们只是来自不同打分体系。

RRF 避开这个问题：不看原始分数，只看每一路检索里的排名。排得越靠前，贡献越大；多路都靠前，贡献会叠加。

## 一个完整例子

假设用户问：

```text
企业版支持 SSO 吗？
```

向量检索返回：

```text
1. faq:login
2. pricing:enterprise
3. intro:security
4. errors:e1024
```

关键词检索返回：

```text
1. pricing:enterprise
2. errors:e1024
3. faq:sso
4. intro:security
```

`pricing:enterprise` 在两路检索里都靠前：

```text
vector rank = 2
keyword rank = 1
```

所以它的总分是：

```text
1 / (60 + 2) + 1 / (60 + 1)
```

`faq:login` 只在向量检索里排第 1，没有出现在关键词结果里，所以它只有一路加分：

```text
1 / (60 + 1)
```

最终 `pricing:enterprise` 会超过 `faq:login`，因为它同时得到了两路检索支持。

## 运行

```bash
uv run advanced/03_production_rag/03_rrf_merge/main.py
```

## 本章要点

- 不同检索器的分数通常不能直接相加。
- RRF 用排名融合，简单稳定。
- RRF 之后得到的是候选集，不一定是最终上下文。
- 生产中常见做法是：多路召回 -> RRF 合并 -> rerank 精排。

## RRF 之后还要做什么

RRF 输出的是“融合候选”，不是最终答案上下文。后面通常还要继续处理：

1. **去重**：同一文档相邻 chunk 可能重复。
2. **metadata filter**：过滤租户、权限、版本、语言。
3. **rerank**：用更精细的模型判断是否直接回答问题。
4. **context packing**：只把最有价值的证据放进 prompt。

一个常见生产链路：

```text
vector top 20 + keyword top 20
  ↓
RRF 融合成候选 30 条
  ↓
metadata filter 去掉无权限和旧版本
  ↓
rerank 取前 5 条
  ↓
组装上下文给 LLM
```

## 常见错误

- 把 `rank` 从 `0` 开始算。RRF 通常按第 1 名为 `rank=1`。
- 以为 `k=60` 是必须值。它只是常用默认值，可以通过评估集调整。
- 融合后不去重，导致同一证据反复进入上下文。
- RRF 后直接把所有候选给 LLM，导致 prompt 太长、噪声太多。
- 忘记保留来源信息，后面无法解释某个结果来自哪一路检索。

## 练习

1. 把 `main.py` 中 `RRF_K` 从 `60` 改成 `10`，观察排名变化。`RRF_K` 越小，靠前排名的影响越大。
2. 把 `pricing:enterprise` 从关键词检索结果里移除，观察它是否还排第一。
3. 新增第三路结果 `metadata_boost_results`，把 `pricing:enterprise` 放第 1，观察多路融合后的变化。
