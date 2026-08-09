# 01 LLM 应用测试

传统测试关注确定性代码；LLM 应用还要测试 prompt、检索、工具调用、Agent 轨迹和模型输出质量。
本章讲如何建立可持续的 AI 应用测试体系。

## 本章要点

- 不要只依赖人工试问几个问题。
- LLM 应用测试要拆成确定性测试和概率性评估。
- Prompt、RAG、Tool、Agent 都需要不同测试方法。
- CI 中应运行轻量评估，完整评估可定时运行。

## 测试金字塔

```text
人工验收 / 红队测试
        ▲
离线评估集：正确性、忠实度、检索质量
        ▲
集成测试：RAG、工具调用、Agent 流程
        ▲
单元测试：解析、切块、权限、参数校验
        ▲
静态检查：类型、lint、配置校验
```

越底层越确定，越上层越接近真实用户。

## 单元测试

适合测试：

- 文档解析函数
- chunk 生成规则
- metadata filter
- prompt 模板变量是否完整
- 工具参数校验
- API 请求/响应模型
- 成本估算函数

示例断言：

```python
def test_metadata_filter_includes_tenant_id():
    filters = build_filters(user)
    assert filters["tenant_id"] == user.tenant_id
```

## Mock LLM

不要让所有测试都真实调用模型。可以用 mock 保证业务流程稳定：

```python
class FakeChatModel:
    def invoke(self, messages):
        return {"content": "mock answer"}
```

适合：

- API 返回格式测试
- 工具调用循环测试
- 错误分支测试
- 超时和重试测试

不适合：

- 模型回答质量测试
- prompt 效果测试
- RAG 忠实度测试

## Golden Tests

Golden test 保存一组输入和期望输出结构。

适合：

- 输出 JSON schema
- 分类任务
- 信息抽取
- 固定格式报告

对于开放式回答，不要要求全文完全一致，应该检查：

- 是否包含关键字段
- 是否引用来源
- 是否拒答越权问题
- 是否没有编造某些内容

## Prompt 回归测试

Prompt 改动后最容易引入隐性回归。建议维护：

```text
eval_cases/
├── prompt_regression.jsonl
├── rag_retrieval.jsonl
└── tool_calling.jsonl
```

每条样本至少包含：

```json
{
  "id": "refund_001",
  "input": "会员买错了能退款吗？",
  "expected_facts": ["7 天内", "提交退款申请"],
  "forbidden_facts": ["30 天内无条件退款"],
  "expected_sources": ["pricing.md", "faq.md"]
}
```

## Tool Calling 测试

工具调用要测试两层：

- 模型是否选择正确工具。
- 工具执行和错误处理是否正确。

测试点：

- 参数缺失
- 参数类型错误
- 权限不足
- 外部系统失败
- 可重试错误
- 不可重试错误
- 高风险操作是否触发人工确认

## Agent 轨迹测试

Agent 的最终答案对了，不代表过程安全。需要检查轨迹：

- 是否调用了禁止工具。
- 是否重复调用同一工具。
- 是否在没有证据时直接回答。
- 是否超过最大步数。
- 是否正确处理工具错误。
- 是否在人机确认前停止。

轨迹样例：

```json
{
  "steps": [
    {"type": "tool_call", "name": "search_docs"},
    {"type": "tool_result", "name": "search_docs"},
    {"type": "final_answer"}
  ]
}
```

## CI 策略

推荐分层运行：

| 阶段 | 内容 | 频率 |
| --- | --- | --- |
| PR | 单元测试、mock 集成测试、小评估集 | 每次提交 |
| Nightly | 完整评估集、RAG 指标、成本统计 | 每天 |
| Release | 回归评估、红队样本、人工抽检 | 发版前 |

CI 中要记录：

- 使用的模型
- prompt 版本
- 知识库版本
- 评估集版本
- 分数变化
- 失败样本 diff

## 常见坑

- 只测 API 200，不测回答是否可信。
- 测试依赖实时模型，导致 CI 不稳定。
- 评估集太小，全是作者自己想的问题。
- Prompt 改动没有版本记录。
- RAG 评估只看答案，不看检索是否命中。

## 具体示例：为退款问答写一条回归测试

评估样本：

```json
{
  "id": "refund_001",
  "input": "我刚买了会员，能退款吗？",
  "expected_facts": ["7 天内", "可以申请退款"],
  "forbidden_facts": ["30 天", "无条件退款"],
  "expected_sources": ["faq.md", "pricing.md"]
}
```

测试思路：

```python
def test_refund_answer_contains_required_facts(rag_app):
    case = load_case("refund_001")
    result = rag_app.answer(case["input"])

    for fact in case["expected_facts"]:
        assert fact in result.answer

    for fact in case["forbidden_facts"]:
        assert fact not in result.answer

    source_names = {source.name for source in result.sources}
    assert "faq.md" in source_names
```

如果模型输出是：

```text
可以，购买后 30 天内无条件退款。
```

这个测试会失败，因为它包含 forbidden fact。相比“答案看起来通顺”，这种测试更能抓住业务风险。

对开放式回答，不要要求全文完全一致；要检查关键事实、禁止事实、引用来源和输出结构。

## 实践任务

为 [tutorials/20_capstone](../../../tutorials/20_capstone/) 增加测试计划：

1. 单元测试：知识库加载、检索、配置读取。
2. Mock 测试：聊天接口不调用真实模型也能返回流。
3. RAG 评估：检查 Top-K 是否命中期望文档。
4. 回答评估：用 LLM judge 判断忠实度。
5. CI 策略：PR 跑小集合，夜间跑完整集合。
