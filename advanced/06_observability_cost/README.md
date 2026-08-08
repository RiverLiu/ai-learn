# 06 观测与成本

观测与成本应该放在同一组学习，因为线上问题定位和成本控制依赖同一批基础数据：trace、token、延迟、模型、prompt 版本、知识库版本和用户反馈。

## 章节目录

1. [01_request_tracing](./01_request_tracing/)：日志、trace、检索链路和线上问题定位
2. [02_feedback_loop](./02_feedback_loop/)：从用户点踩到评估样本的闭环
3. [03_token_cost_latency](./03_token_cost_latency/)：token 成本、缓存、限流、fallback 和延迟优化

## 学习目标

- 能设计一次请求的 trace 结构。
- 能定位 RAG 失败发生在哪个阶段。
- 能把用户反馈沉淀为评估样本。
- 能按阶段统计 token 和延迟。
