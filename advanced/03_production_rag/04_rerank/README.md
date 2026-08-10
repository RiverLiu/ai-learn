# 04 Rerank 精排

第一阶段检索的目标是“尽量多召回”，rerank 的目标是“从候选里选最相关的少数证据”。

不要把 rerank 当成召回替代品。如果第一阶段没有召回正确 chunk，rerank 没有东西可排。

## Rerank 是什么

Rerank 可以理解为“二次排序”：

```text
用户问题 + 第一阶段召回的候选 chunks -> reranker -> 重新排序后的 chunks
```

第一阶段检索通常追求召回率，会多拿一些候选，例如 `top_k=20`。这些候选里可能包含：

- 真正能回答问题的 chunk。
- 主题相近但答不上问题的 chunk。
- 包含同一个关键词但语义不相关的 chunk。
- 旧版本、重复段落、上下文不完整的 chunk。

rerank 的任务是逐条判断“这个 chunk 对当前问题到底有多有用”，然后把最有用的证据排到前面。

## 一个直观例子

用户问：

```text
企业版支持 SSO 吗？其他版本支持吗？
```

第一阶段检索可能返回：

```text
1. intro:security
   云雀笔记提供权限管理、数据加密和团队协作能力。

2. faq:login
   云雀笔记支持手机号、邮箱和第三方账号登录。

3. pricing:enterprise
   企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。

4. security:audit
   审计日志会记录成员登录、导出、删除和权限变更操作。
```

这些结果都和“安全、登录、企业能力”有关，但只有 `pricing:enterprise` 直接回答了两个关键点：

- 企业版是否支持 SSO。
- 其他版本是否支持 SSO。

rerank 后应该变成：

```text
1. pricing:enterprise
2. faq:login
3. intro:security
4. security:audit
```

进入 LLM 的上下文就可以只取前 1 到 2 条，减少噪声和 token 成本。

## Rerank 和普通检索的区别

| 阶段 | 目标 | 输入 | 输出 | 关注点 |
| --- | --- | --- | --- | --- |
| 召回 | 尽量别漏 | 用户问题、索引 | 候选 chunks | 召回率、覆盖面 |
| rerank | 排得更准 | 用户问题、候选 chunks | 重排后的 chunks | 相关性、可回答性 |

一个实用判断：

```text
召回问：“这个 chunk 可能相关吗？”
rerank 问：“这个 chunk 能直接支撑答案吗？”
```

## 常见实现方式

| 方式 | 说明 | 适合场景 |
| --- | --- | --- |
| 专用 rerank API | 调用商业或开源服务，对 query-document pair 打分 | 生产常用，接入简单 |
| cross-encoder | 把问题和 chunk 拼在一起输入模型，输出相关性分数 | 精度较好，延迟比 embedding 高 |
| bge-reranker 系列 | 常见开源 reranker 模型 | 本地部署、私有化场景 |
| LLM rerank | 让 LLM 判断候选相关性并排序 | 候选少、低频、高价值任务 |
| 规则 rerank | 用关键词、字段、时间、权限、文档类型加权 | 业务规则明确的场景 |

本章脚本用的是“规则 rerank”，目的是让你看清 rerank 的输入、输出和效果。真实生产中可以把规则函数替换成专门 reranker。

## 生产中的输入输出

一个 rerank 请求通常长这样：

```json
{
  "query": "企业版支持 SSO 吗？其他版本支持吗？",
  "documents": [
    "云雀笔记提供权限管理、数据加密和团队协作能力。",
    "云雀笔记支持手机号、邮箱和第三方账号登录。",
    "企业版支持 SSO、审计日志和专属客户成功经理。个人版和团队版不包含 SSO。"
  ],
  "top_n": 2
}
```

输出通常是文档下标和相关性分数：

```json
[
  {"index": 2, "score": 0.94},
  {"index": 1, "score": 0.31}
]
```

工程上要把 `index` 映射回原始 `chunk_id`、`source`、`page`、`updated_at`，否则后面无法引用和排查。

## 运行

```bash
uv run advanced/03_production_rag/04_rerank/main.py
```

## 本章要点

- 召回阶段可以取 `top_k=20` 或更多，避免漏掉候选。
- rerank 阶段再取 `top_n=3` 到 `top_n=5`，控制进入 LLM 的上下文。
- rerank 更关注“这段是否直接回答当前问题”，不是只看主题相似。
- LLM rerank 成本高、延迟大，适合低频高价值任务；高频场景通常用专门 reranker。

## 什么时候需要 rerank

适合加入 rerank：

- Top-K 里经常有正确 chunk，但没有排在前面。
- 用户问题包含多个条件，例如“企业版支持 SSO 吗？其他版本呢？”。
- 向量检索召回了主题相近但不能回答问题的段落。
- Hybrid Search 合并后候选较多，需要再精排。
- 上下文太长、成本太高，需要从 20 条候选里只选 3 到 5 条。

不适合一开始就加 rerank：

- Top-K 根本没有正确资料。此时应该先修切块、embedding、query rewrite 或 hybrid search。
- 数据权限没有处理。rerank 不能替代 metadata filter。
- 评估集还没有建立。没有评估集就很难判断 rerank 是否真的提升质量。

## 常见错误

- 把 rerank 当成“召回增强”。rerank 只能重排已有候选，不能凭空找到没召回的资料。
- 召回 `top_k` 太小。候选太少时，rerank 没有发挥空间。
- rerank 后仍然把所有候选塞进 prompt。这样没有降低噪声和成本。
- 只看 rerank 分数，不看最终答案是否忠实引用证据。
- 对所有请求都用 LLM rerank，导致延迟和成本过高。

## 观察点

脚本里的初始候选都和“企业安全能力”相关，但只有一条直接回答“企业版是否支持 SSO，以及其他版本是否支持”。rerank 会把直接答案排到前面。

运行后重点看两段输出：

```text
第一阶段召回顺序
```

这里展示“主题相关但排序不准”的原始候选。

```text
rerank 后
```

这里展示 reranker 如何把直接答案排到最前面。

## 练习

1. 把 `main.py` 里的问题改成“审计日志记录哪些操作？”，观察当前规则 rerank 是否还合理。
2. 给 `rerank_score()` 增加一条规则：如果问题里出现“审计日志”，包含“审计日志”的 chunk 加 4 分。
3. 把进入 LLM 的上下文从前 2 条改成前 1 条，思考答案完整性和成本的变化。
