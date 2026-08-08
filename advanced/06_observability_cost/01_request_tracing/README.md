# 01 请求链路追踪与日志

AI 应用上线后，最常见的问题不是“接口挂了”，而是“用户觉得答得不对，但你不知道哪里错了”。
可观测性要让你能回答：请求发生了什么、检索到了什么、模型看到了什么、调用了什么工具、花了多少钱、为什么失败。

## 本章要点

- 每次请求都应该有 trace id。
- 日志要覆盖模型调用、检索、工具调用、成本和用户反馈。
- 线上失败样本应该能回流到评估集。
- 可观测性不是只接 LangSmith，也包括业务日志和数据库记录。

## 关键观测对象

| 对象 | 需要记录什么 |
| --- | --- |
| 请求 | user_id、tenant_id、session_id、trace_id、入口、耗时 |
| Prompt | prompt 版本、模板名、变量摘要、上下文长度 |
| LLM | model、input_tokens、output_tokens、latency、finish_reason |
| RAG | query、rewrite query、top_k、命中文档、score、引用 |
| Tool | 工具名、参数摘要、权限结果、耗时、错误 |
| Agent | step 数、轨迹、停止原因、是否人工确认 |
| 反馈 | 点赞/点踩、用户评论、是否解决、人工标注 |

## Trace 结构

推荐每个用户请求形成一棵 trace：

```text
chat_request trace_id=abc
├── auth_check
├── load_session
├── rewrite_query
├── retrieve_documents
│   ├── vector_search
│   └── rerank
├── build_prompt
├── llm_stream
└── save_message
```

这样线上问题可以定位到具体阶段：

- 检索没命中。
- rerank 排错。
- prompt 上下文过长。
- 模型超时。
- 工具调用失败。
- 数据库存储失败。

## 日志字段设计

推荐结构化日志：

```json
{
  "timestamp": "2026-08-08T10:00:00+08:00",
  "level": "INFO",
  "event": "llm_call_completed",
  "trace_id": "abc",
  "session_id": "s_001",
  "model": "gpt-4.1",
  "input_tokens": 1200,
  "output_tokens": 280,
  "latency_ms": 1800,
  "cost_usd": 0.012
}
```

注意不要把敏感原文无脑写进日志。生产环境要区分：

- 可长期保存的摘要字段
- 短期排障日志
- 脱敏后的样本
- 需要权限才能访问的原始 prompt

## 用户反馈闭环

最小闭环：

```text
用户点踩
  ↓
保存问题、答案、引用、trace_id、用户评论
  ↓
人工标注失败原因
  ↓
加入评估集
  ↓
修复 prompt / 检索 / 数据 / 工具
  ↓
回归评估
```

反馈不要只存一个 `like=false`，至少保存：

- 用户问题
- 模型回答
- 检索来源
- prompt 版本
- 知识库版本
- 用户评论
- 失败类型

## 指标面板

建议看板：

- QPS / 请求量
- p50 / p95 / p99 延迟
- token 成本
- 单次请求平均成本
- 模型错误率
- 检索无结果率
- 工具调用失败率
- 用户点踩率
- 人工接管率
- 超时率

AI 质量指标：

- RAG 命中文档率
- 引用点击率
- 追问率
- 拒答正确率
- 评估集通过率

## 常见坑

- 只记录最终答案，不记录检索上下文，无法定位 RAG 问题。
- 日志里没有 prompt 版本，改了 prompt 后无法对比。
- 用户反馈没有 trace_id，无法复现。
- 记录了完整敏感信息，造成二次泄露风险。
- 只看平均延迟，不看 p95/p99。

## 具体示例：一次点踩如何回流到评估集

用户点踩时，前端提交：

```json
{
  "message_id": "msg_1024",
  "rating": "down",
  "comment": "退款时间说错了"
}
```

后端根据 `message_id` 查到完整链路：

```json
{
  "trace_id": "trace_abc",
  "question": "会员买错了能退吗？",
  "answer": "购买后 30 天内可以退款。",
  "prompt_version": "customer_support_v3",
  "kb_version": "kb_2026_08_01",
  "retrieved_sources": [
    {"source": "faq.md", "section": "退款规则", "score": 0.81}
  ],
  "model": "gpt-4.1-mini",
  "input_tokens": 980,
  "output_tokens": 120
}
```

人工标注失败类型：

```json
{
  "failure_type": "answer_not_faithful_to_context",
  "expected_fact": "购买后 7 天内可以申请退款",
  "wrong_fact": "购买后 30 天内可以退款"
}
```

转成评估样本：

```json
{
  "id": "feedback_refund_20260808_001",
  "input": "会员买错了能退吗？",
  "expected_facts": ["7 天内", "可以申请退款"],
  "forbidden_facts": ["30 天内可以退款"],
  "expected_sources": ["faq.md"]
}
```

这样线上差评不会停留在“用户不满意”，而是变成下一次发版必须通过的回归样本。

## 实践任务

为 [tutorials/capstone](../../../tutorials/capstone/) 设计日志表：

- `chat_messages`
- `llm_calls`
- `retrieval_events`
- `tool_calls`
- `user_feedback`

每张表列出关键字段，并说明哪些字段需要脱敏。
