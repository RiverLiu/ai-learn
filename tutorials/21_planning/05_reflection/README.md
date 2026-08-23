# 05 Reflection：执行后自我检查与修订

Reflection 指 Agent 在完成一次生成或工具执行后，主动检查结果，找出缺陷，再修订输出。

典型流程：

```text
Draft -> Evaluate -> Critique -> Revise -> Final
```

它解决的问题不是“怎么规划步骤”，而是“做完以后怎么发现自己哪里没做好”。

## 本章要点

- **Draft**：先生成一个可检查的初稿，哪怕它不完美。
- **Evaluate**：用明确评分表检查事实、完整性和引用。
- **Critique**：把问题变成可执行的修订清单。
- **Revise**：只基于已有 evidence 修订，不能编造新事实。
- **Stop rule**：达到目标分数或最大反思次数后停止。

## 运行

本章是离线示例，不调用模型 API：

```bash
uv run tutorials/21_planning/05_reflection/main.py
```

## 教学场景

用户问：

```text
专业版和团队版有什么区别？我适合哪个？
```

知识库证据包含：

```text
[pricing:pro] 专业版每月 29 元，支持历史版本保留 180 天。
[pricing:pro] 专业版支持最多 10 个协作者共同编辑笔记。
[pricing:team] 团队版每月 99 元，支持最多 50 个成员。
[faq:team_admin] 团队版提供管理员转让、成员权限管理和统一账单。
[faq:refund] 购买后 7 天内可以申请退款。
```

初稿故意写得不完整：

```text
专业版每月 29 元，适合个人使用；团队版适合团队使用。
```

这个初稿有三个典型问题：

- 漏掉团队版价格。
- 漏掉专业版协作者上限和团队版管理能力。
- 没有引用来源。

Reflection 的价值就是把“感觉不完整”变成明确问题清单，再按证据修订。

## 评分表

脚本用 10 分制评估每一轮输出：

| 维度 | 分值 | 检查内容 |
| --- | --- | --- |
| factuality | 4 | 是否出现无证据支持或错误事实 |
| completeness | 4 | 是否覆盖必须回答的关键事实 |
| citation | 2 | 是否引用支持答案的来源 |

输出示例：

```text
Score: factuality=4/4, completeness=1/4, citation=0/2, total=5/10
Issues:
- 缺少事实：pro_collaboration
- 缺少事实：team_price
- 缺少事实：team_admin
- 缺少引用：faq:team_admin, pricing:pro, pricing:team
```

这比只打印 `Draft / Critique / Final` 更有体感：学员能看到分数如何变化，也能看到每个问题对应哪类质量缺陷。

## 多轮 Reflection

脚本会执行最多 `max_rounds` 轮：

```text
Draft
  ↓
Evaluate + Critique
  ↓
Revise
  ↓
Evaluate + Critique
  ↓
达到 target_score 或最大轮数后停止
```

停止条件很重要。没有停止条件时，Agent 可能一直“自我反思”，造成成本和延迟失控。

本章示例默认：

```python
run_reflection(max_rounds=2, target_score=8)
```

含义是：最多修订 2 次；如果总分达到 8 分，就不再继续。

## 三种 Reflection

| 模式 | 检查什么 | 示例 |
| --- | --- | --- |
| Answer Reflection | 答案是否事实正确、完整、有引用 | 客服答案漏掉套餐限制 |
| Tool Reflection | 工具执行结果是否满足目标 | 搜索结果不够，需要换关键词再查 |
| Plan Reflection | 当前计划是否还合理 | 执行失败后触发 Replanning |

本章重点演示 Answer Reflection。它可以和其他章节组合：

```text
ReAct 查资料 -> Draft 答案 -> Reflection 检查 -> 不足则继续 ReAct 或 Replanning
```

## 证据不足不能编造

Reflection 不是让模型“想办法补齐答案”。它只能基于已有 evidence 修订。

例如把 `team_price` 证据拿掉后，脚本会输出：

```text
资料不足：team_price 暂时不能确认。
```

而不是编造：

```text
团队版每月 99 元。
```

这条规则在 RAG、客服、法务、医疗、财务场景尤其重要：证据不足时应该拒答、提示缺资料，或触发下一轮检索。

## 运行后观察点

运行脚本后重点看四段：

```text
Evidence
```

确认修订只能使用这些资料。

```text
Draft
```

观察初稿的漏项和无引用问题。

```text
Reflection Round 1
```

观察修订后分数是否提升、issue 是否减少。

```text
反例：证据不足时不能编造
```

观察缺少团队版价格证据时，最终答案如何明确说明资料不足。

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 反思只说“挺好” | 没有检查标准 | 明确评分维度和必须覆盖的事实 |
| 无限反思 | 没有停止条件 | 设置 `max_rounds` 和 `target_score` |
| 修订引入新事实 | 没有限制 evidence | Revise 只能使用已有证据 |
| 只改文风不改事实 | critique 太泛 | 检查 factuality、completeness、citation |
| 反思后仍不可审计 | 没有引用来源 | 要求答案绑定 source id |

## 练习建议

1. 把 `target_score` 从 `8` 改成 `10`，观察是否需要更多轮修订。
2. 删除 `team_admin` 证据，观察最终答案是否会说明资料不足。
3. 在 `FORBIDDEN_UNSUPPORTED_FACTS` 中增加“团队版支持无限成员”，再把它加入初稿，观察 factuality 分数变化。
4. 把本章和 `00_react` 组合：当 Reflection 发现 `证据不足` 时，触发一次新的 `search_docs()`。
5. 思考 Reflection 和 `03_replanning` 的区别：Reflection 修订输出，Replanning 调整后续行动。
