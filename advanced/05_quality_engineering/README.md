# 05 质量工程

质量工程关注如何证明 AI 应用“没有因为一次 prompt、模型、知识库或代码改动而变差”。

## 章节目录

1. [01_llm_testing](./01_llm_testing/)：LLM mock、golden tests、tool calling 和 Agent 轨迹测试
2. [02_eval_ci](./02_eval_ci/)：把评估集接入 CI，区分 PR、nightly 和 release 评估
3. [03_prompt_regression](./03_prompt_regression/)：Prompt 版本、回归样本和失败 diff

## 学习目标

- 能区分确定性测试和模型质量评估。
- 能为 RAG 问答写 expected facts / forbidden facts。
- 能设计 CI 中的轻量评估。
- 能用线上反馈补充回归集。
