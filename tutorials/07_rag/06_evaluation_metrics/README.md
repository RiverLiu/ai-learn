# 06 RAG 评估指标

RAG 做出来以后，不能只靠"看起来回答得还行"判断质量。一个完整的 RAG 问答链路至少包含
检索、上下文拼接、生成、引用和线上反馈，任何一环失败都会让最终答案变差。

本章把 RAG 评估拆成四类指标：检索指标、生成指标、引用指标、线上指标。学完以后，你应该能回答：

- 是检索没有找到正确资料，还是模型拿到资料后没有答好？
- Top-K、切块、rerank、prompt 调整后，质量是否真的提升？
- 答案引用是否支持结论，还是只是在末尾挂了几个来源？
- 系统上线后应该持续观察哪些指标？

## 本章要点

- **先评估检索，再评估生成**：如果 Top-K 里没有正确资料，生成模型再强也只能猜。
- **离线指标用于迭代配置**：例如对比不同 chunk size、embedding 模型、Top-K、rerank 策略。
- **引用指标用于约束可信度**：RAG 不只是答对，还要能指出答案来自哪里。
- **线上指标用于发现真实问题**：离线评估集覆盖不了所有问法，需要结合用户反馈和日志持续优化。

## 运行

本章脚本不调用模型 API，使用固定的模拟检索结果演示指标计算：

```bash
uv run tutorials/07_rag/06_evaluation_metrics/main.py
```

你会看到每个问题的检索命中情况，以及整体的 `Hit Rate@K`、`Recall@K`、`MRR`、引用精确率和引用召回率。

## 评估对象

RAG 评估不要只评最终答案。建议把一次请求拆成以下对象：

```text
用户问题
  ↓
查询改写 / embedding
  ↓
检索 Top-K chunks
  ↓
rerank / context packing
  ↓
LLM 生成答案
  ↓
引用来源 / 拒答 / 线上反馈
```

每一层都有自己的指标：

| 层级 | 关键问题 | 常用指标 |
| --- | --- | --- |
| 检索 | 正确资料是否进了 Top-K？排序是否靠前？ | Hit Rate@K、Recall@K、Precision@K、MRR、nDCG |
| 生成 | 答案是否正确、完整、忠实于资料？ | Correctness、Faithfulness、Answer Relevance、Completeness |
| 引用 | 引用是否覆盖答案结论？是否引用了无关来源？ | Citation Precision、Citation Recall、Unsupported Claim Rate |
| 线上 | 用户是否解决问题？成本和延迟是否可接受？ | 点踩率、追问率、转人工率、p95 延迟、单问成本 |

## 检索指标

检索评估集的最小格式：

```json
{
  "question": "专业版支持多少个协作者？",
  "expected_doc_ids": ["pricing"],
  "expected_chunk_ids": ["pricing:pro"],
  "retrieved_chunk_ids": ["pricing:pro", "faq:share", "intro:sync"]
}
```

### Hit Rate@K

只判断前 K 个结果里是否至少命中一个正确 chunk。

```text
Hit@K = 1 if Top-K 中包含任意 expected_chunk，否则为 0
Hit Rate@K = 所有问题的 Hit@K 平均值
```

适合回答："Top-3 是否至少找到了一个有用证据？"

### Recall@K

当一个问题需要多个证据时，Hit Rate 不够。Recall@K 关注应该找到的证据找回了多少。

```text
Recall@K = Top-K 命中的正确 chunk 数 / expected_chunk 总数
```

例如用户问"免费版和专业版的历史版本保留时间有什么区别"，需要同时命中免费版和专业版两个 chunk。
如果 Top-5 只找到了免费版，`Recall@5 = 1 / 2 = 0.5`。

### Precision@K

Precision@K 关注 Top-K 中有多少结果是有用的。

```text
Precision@K = Top-K 命中的正确 chunk 数 / K
```

它适合衡量上下文噪声。Top-K 中无关 chunk 太多，会挤占 prompt 空间，也会诱导模型答偏。

### MRR

MRR（Mean Reciprocal Rank）关注第一个正确结果排第几。

```text
单个问题 RR = 1 / 第一个正确结果的排名
MRR = 所有问题 RR 的平均值
```

如果正确 chunk 排第 1，得 1.0；排第 2，得 0.5；排第 5，得 0.2；没找到，得 0。
它比 Hit Rate 更能体现排序质量。

### nDCG

nDCG 会给不同相关性等级打分，例如完全相关、部分相关、无关，并考虑排序位置。
基础教程里先知道它的用途即可：当你不仅关心"是否命中"，还关心"强相关结果是否排在前面"，可以使用 nDCG。

## 生成指标

检索命中以后，仍然可能出现生成失败。常见生成指标包括：

| 指标 | 评估问题 | 典型判定 |
| --- | --- | --- |
| Correctness | 答案事实是否正确？ | 是否和参考答案或标准事实一致 |
| Faithfulness | 答案是否只基于上下文？ | 是否出现上下文没有支持的断言 |
| Answer Relevance | 答案是否回答了用户问题？ | 是否绕题、泛泛而谈、答非所问 |
| Completeness | 关键信息是否完整？ | 是否漏掉限制条件、价格、时间、适用范围 |
| Refusal Accuracy | 无资料时是否正确拒答？ | 应拒答时拒答，不应拒答时正常回答 |

一个实用做法是给每条样本保存：

```json
{
  "question": "云雀笔记免费版支持多少台设备同步？",
  "retrieved_context": ["免费版支持最多 2 台设备同步。"],
  "answer": "免费版最多支持 2 台设备同步。",
  "reference_answer": "免费版支持最多 2 台设备同步。",
  "expected_behavior": "answer"
}
```

然后用人工抽检或 LLM judge 给出结构化分数。注意：LLM judge 的提示词、模型版本和判分标准也要固定，否则指标会漂移。

## 引用指标

RAG 答案里的引用必须能支持具体结论。只要在末尾堆几个来源，并不等于可信。

### Citation Precision

引用精确率衡量"引用的来源有多少是真的相关"。

```text
Citation Precision = 正确引用数 / 输出引用总数
```

如果答案引用了 3 个来源，其中只有 2 个真正支持答案，引用精确率是 `2 / 3`。

### Citation Recall

引用召回率衡量"应该引用的关键来源是否都引用了"。

```text
Citation Recall = 正确引用数 / 应引用来源总数
```

如果一个答案需要同时引用价格文档和 FAQ，但只引用了价格文档，引用召回率是 `1 / 2`。

### Unsupported Claim Rate

Unsupported Claim Rate 衡量答案中没有证据支持的断言比例。

```text
Unsupported Claim Rate = 无支持断言数 / 总断言数
```

例如上下文只说"专业版每月 29 元"，模型却回答"专业版每月 29 元，并提供企业级 SSO"。
"提供企业级 SSO"就是无支持断言。

## 线上指标

离线评估只能覆盖你提前想到的问题，上线后还要持续观察真实用户行为：

- **点踩率 / 负反馈率**：用户直接认为答案不好。
- **追问率**：用户频繁追问同一问题，可能说明答案不完整。
- **转人工率**：客服场景下，RAG 未解决问题的比例。
- **无结果率**：检索结果低于阈值，或者系统主动拒答。
- **p50 / p95 延迟**：平均快不代表体验稳定，p95 更接近用户感知。
- **单问成本**：embedding、rerank、LLM 输入输出 token、日志存储都要算。
- **引用点击率**：用户是否打开来源验证答案，能反映引用是否有用。

线上指标要和日志样本打通。看到点踩率升高时，要能追溯到：用户问题、Top-K、上下文、最终答案、引用来源和模型配置。

## 常见失败与指标定位

| 现象 | 优先看什么指标 | 可能原因 |
| --- | --- | --- |
| 答案完全答非所问 | Hit Rate@K、MRR | embedding 不合适、chunk 太碎、查询改写失败 |
| 答案漏掉限制条件 | Recall@K、Completeness | 需要多证据但只召回一部分 |
| 答案有编造内容 | Faithfulness、Unsupported Claim Rate | prompt 约束弱、上下文噪声、模型过度补全 |
| 引用来源看起来无关 | Citation Precision | 引用生成逻辑粗糙，或检索结果本身无关 |
| 回答慢且贵 | p95 延迟、单问成本 | Top-K 过大、rerank 过重、上下文太长 |
| 离线分数高但线上差 | 线上负反馈、追问率 | 评估集太理想化，没有覆盖真实问法 |

## 评估集设计建议

一套基础 RAG 评估集建议包含：

- **事实查询**：答案直接来自一个 chunk。
- **多证据查询**：需要合并多个 chunk。
- **边界问题**：知识库没有答案，应该拒答。
- **口语化问题**：用户不会照抄文档原文。
- **近义混淆问题**：多个文档相似，考验排序和引用。
- **时效问题**：文档更新后，验证旧答案是否消失。

每条样本至少记录：

```json
{
  "id": "rag-eval-001",
  "question": "学生买专业版有什么优惠？",
  "expected_chunk_ids": ["pricing:student_discount"],
  "reference_answer": "学生凭 edu 邮箱可申请专业版半价优惠。",
  "must_cite": ["pricing"],
  "should_refuse": false
}
```

## 指标使用顺序

调试 RAG 时建议按这个顺序看：

1. **打印 Top-K**：肉眼确认是否召回正确内容。
2. **看 Hit Rate@K / Recall@K**：判断召回率是否足够。
3. **看 MRR / nDCG**：判断正确内容是否排得足够靠前。
4. **看 Faithfulness / Unsupported Claim Rate**：判断模型是否忠实于上下文。
5. **看 Citation Precision / Recall**：判断引用是否真的支撑答案。
6. **看线上负反馈和延迟成本**：判断用户体验和生产可行性。

不要一上来就改 prompt。很多 RAG 问题的根因在检索和数据，不在生成。

## 与评估教程的关系

本章是 RAG 学习阶段的指标入门，重点是理解每类指标解决什么问题。

更系统的实验对比请继续学习：

- [15_evaluation/03_rag_metrics](../../15_evaluation/03_rag_metrics/)：用真实 embedding 对比切块配置的检索质量。
- [advanced/03_production_rag](../../../advanced/03_production_rag/)：生产级 RAG 的召回、重排、上下文压缩与质量治理。

## 练习

1. 给 `knowledge_base/` 设计 10 条评估问题，并标出每条问题应该命中的 `document_id`。
2. 把 `main.py` 中的 `TOP_K` 从 3 改成 1，观察 Hit Rate 和 Recall 的变化。
3. 增加一条"知识库没有答案"的问题，设计一个拒答准确率指标。
