# LLM 应用评估（Evaluation）教程

改了一句提示词、换了一个模型、调了一下 chunk 大小——"效果有没有变好？"
没有评估，这类问题永远只能靠"跑两条看看感觉"，这就是玩具和产品的分水岭。

**评估是 AI 工程化的分水岭**：传统软件有单元测试做回归，LLM 应用输出不确定，
评估集 + 指标就是它的回归测试。没有评估的调参是蒙眼开车：每次改动可能变好、
可能变坏，你无法知道，更无法向别人证明。有了评估，每次改动都变成一个可回答的问题：
"重跑评估集，分数涨了还是跌了？"

## 评估的三层基本功（对应三章）

1. **评估集**：没有数据就没有评估。题目怎么写、字段怎么设计、怎么避免自欺欺人。
2. **评估方法**：字面匹配（关键词）为什么不够用，LLM-as-judge 的 rubric 怎么设计、
   结果怎么解析、judge 本身可不可信。
3. **分层指标**：RAG 系统要把检索和生成**分开**评估——检索有干净的程序化指标
   （命中率），生成才需要 judge。答非所问时先查哪一环，评估结果会直接告诉你。

## 与 tutorials/langchain/06_langsmith 的关系

[06_langsmith](../langchain/06_langsmith/) 讲的是**平台**：怎么用 LangSmith 存 dataset、
跑评估、看 trace。本模块讲的是**方法**：评估集怎么构建、指标怎么算、judge 怎么设计——
这些方法不依赖任何平台，三章全部只用 OpenAI SDK + numpy 手写实现。
学会方法之后，换 LangSmith、Langfuse 或任何评估平台，只是换个"跑评估的壳"。

## 章节目录

1. [01_eval_dataset](./01_eval_dataset/)：评估集构建——围绕"云雀笔记"知识库写 10 条 QA 评估集，
   用关键词命中率打分，并证明它不靠谱
2. [02_llm_judge](./02_llm_judge/)：LLM-as-judge——定义正确性/忠实度 rubric，
   judge 逐条打分，用"差提示词"验证评估能区分好坏
3. [03_rag_metrics](./03_rag_metrics/)：检索质量评估——Top-K 命中率，
   对比不同 chunk 大小下的命中率，用数据驱动调参

第 1、2 章共用 `01_eval_dataset/data/eval_qa.jsonl` 这份评估集；第 3 章使用独立的
检索评估集。三章共用 rag 教程的示例知识库（[../rag/knowledge_base](../rag/knowledge_base/)）。

## 环境准备

依赖已包含在项目根目录的 `pyproject.toml` 中（`openai`、`numpy`），执行：

```bash
uv sync
```

第 1、2 章需要聊天模型，第 3 章需要 Embedding 模型，先配置密钥：

```bash
export OPENAI_API_KEY="sk-..."
# 使用兼容 OpenAI 协议的服务时追加：
export OPENAI_BASE_URL="https://..."
export MODEL_NAME="..."        # 聊天模型，默认 gpt-4o-mini（第 1、2 章）
export EMBEDDING_MODEL="..."   # 向量模型，默认 text-embedding-3-small（第 3 章）
```

建议先完成 [rag 教程](../rag/)（知识库与切块、检索概念都来自那里），
[langchain 教程 04_rag](../langchain/04_rag/) 亦可作为背景参考。

## 参考

- RAG 评估框架 RAGAS 的指标设计：https://docs.ragas.io/（本模块手工实现了它的核心思想）
- OpenAI Evals：https://github.com/openai/evals
- DeepEval（开源评估框架）：https://github.com/confident-ai/deepeval
