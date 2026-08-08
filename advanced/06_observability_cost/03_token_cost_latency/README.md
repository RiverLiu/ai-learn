# 03 Token 成本与延迟优化

AI 应用的性能问题通常来自三个地方：模型调用慢、上下文太长、外部工具或检索链路不稳定。
成本问题通常来自 token 浪费、重复 embedding、无缓存和模型选型过度。

## 本章要点

- 优化前先量化：latency、token、QPS、cache hit rate。
- 成本优化不是一味换小模型，而是减少无效上下文和重复计算。
- 性能优化要区分流式体验和真实完成时间。
- 限流、超时、重试和 fallback 是生产系统的基本能力。

## 成本构成

```text
总成本 =
  聊天模型输入 token
+ 聊天模型输出 token
+ embedding token
+ rerank 成本
+ 语音/图像模型成本
+ 向量库/数据库/对象存储成本
+ 失败重试成本
```

常见浪费：

- 每轮都塞完整历史。
- RAG 拼入过多无关 chunk。
- 重复 embedding 同一文档。
- 小任务使用过强模型。
- JSON 输出太啰嗦。
- 失败后无上限重试。

## 延迟分解

```text
总延迟 =
  鉴权
+ 会话读取
+ query rewrite
+ 检索
+ rerank
+ prompt 组装
+ LLM first token
+ LLM streaming
+ 数据保存
```

前端用户感知通常更关心：

- first token latency
- 中途是否持续输出
- 总完成时间
- 失败后是否有明确反馈

## 优化手段

### 上下文裁剪

原则：

- 会话历史按任务相关性保留，不是按时间盲目保留。
- RAG chunk 先 rerank 再拼。
- 长文档用摘要或父子 chunk。
- 工具结果只保留必要字段。

### 缓存

缓存类型：

| 类型 | 适合缓存什么 |
| --- | --- |
| embedding cache | 文档 chunk、常见查询 |
| retrieval cache | 高频相同问题 |
| prompt prefix cache | 稳定系统提示词和长上下文 |
| tool result cache | 天气、汇率、配置等短期稳定结果 |
| final answer cache | FAQ 类固定答案 |

注意缓存失效：

- 知识库更新
- 权限变化
- 用户上下文变化
- 模型版本变化
- prompt 版本变化

### 模型路由

不同任务用不同模型：

| 任务 | 推荐 |
| --- | --- |
| 简单分类 | 小模型 |
| query rewrite | 小模型或规则 |
| 最终复杂回答 | 强模型 |
| JSON 抽取 | 支持结构化输出的模型 |
| 高风险工具决策 | 强模型 + 规则校验 |

不要让所有任务都走最贵模型。

### 超时和重试

建议：

- 给每个外部调用设置 timeout。
- 区分可重试和不可重试错误。
- 使用指数退避。
- 设置最大重试次数。
- 对流式接口处理半路断开。
- 对长任务提供异步状态查询。

### 限流

限流维度：

- IP
- user_id
- tenant_id
- API key
- 模型
- 工具
- 总 token

限流响应要清楚告诉用户：

- 当前限制类型
- 何时可以重试
- 是否可以降级处理

## 常见坑

- 只优化模型速度，忽略检索和 rerank 延迟。
- 没有 token 统计，成本上涨后不知道原因。
- 缓存没有纳入权限，导致越权复用答案。
- 失败重试把成本打爆。
- 为了省钱换小模型，但没有评估质量下降。

## 具体示例：一次请求的成本账单

一次客服问答的链路：

```text
query rewrite：输入 120 tokens，输出 30 tokens
RAG 上下文：3 个 chunk，共 1,500 tokens
最终回答：输入 1,900 tokens，输出 260 tokens
```

如果只看最终回答，会误以为成本来自“回答太长”。实际大头可能是 RAG 上下文。

优化前：

```json
{
  "rewrite_input_tokens": 120,
  "rewrite_output_tokens": 30,
  "answer_input_tokens": 1900,
  "answer_output_tokens": 260,
  "retrieved_chunks": 8,
  "used_chunks": 8
}
```

优化策略：

- 检索 top_k 从 8 降到 20 召回后 rerank 取 4，不是直接拼 8 个。
- 删除重复 chunk。
- 对 FAQ 类问题缓存最终答案。
- query rewrite 使用小模型。

优化后：

```json
{
  "rewrite_input_tokens": 120,
  "rewrite_output_tokens": 30,
  "answer_input_tokens": 980,
  "answer_output_tokens": 220,
  "retrieved_chunks": 20,
  "used_chunks": 4,
  "cache_hit": false
}
```

这个例子说明：成本优化要记录分阶段 token，否则不知道该优化模型、检索还是 prompt。

## 实践任务

为任意一个 LLM API 示例增加成本统计：

1. 记录 input token、output token。
2. 估算单次请求成本。
3. 输出总耗时和 first token latency。
4. 加入最大重试次数。
5. 对 prompt 版本和模型名打日志。
