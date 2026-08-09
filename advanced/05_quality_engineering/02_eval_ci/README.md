# 02 评估接入 CI

LLM 应用的 CI 不应该只跑单元测试，还应该跑小规模评估集，防止 prompt、检索和模型配置回归。

## 推荐分层

| 阶段 | 内容 |
| --- | --- |
| PR | 单元测试、mock 测试、10 条核心评估 |
| Nightly | 完整评估集、RAG 指标、成本统计 |
| Release | 红队样本、人工抽检、灰度观察 |

## 输出示例

```text
eval_name: rag_core
model: gpt-4.1-mini
prompt_version: support_v4
pass_rate: 92%
failed_cases:
  - refund_003
  - enterprise_sso_001
```

## 练习

为 `tutorials/15_evaluation` 设计一个 GitHub Actions 流程：PR 跑 10 条样本，夜间跑完整样本。
