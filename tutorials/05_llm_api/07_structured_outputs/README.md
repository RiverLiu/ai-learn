# 07 结构化输出进阶

很多 AI 应用不是要一段自然语言，而是要稳定的 JSON：分类结果、抽取字段、评分、工单标签、工具参数。
结构化输出的核心不是“让模型尽量输出 JSON”，而是**定义结构、校验结构、失败时修复或重试**。

## 本章要点

- JSON 格式要求必须写清楚。
- 模型输出需要用 Pydantic 或 JSON Schema 校验。
- 解析失败是正常情况，要有修复和重试策略。
- 结构化输出和 tool calling 相似，但用途不同。

## 运行

本章示例离线运行，使用模拟模型输出演示解析和校验：

```bash
uv run tutorials/05_llm_api/07_structured_outputs/main.py
```

## 示例任务

用户输入：

```text
我买错了专业版，昨天刚付款，能退款吗？
```

期望输出：

```json
{
  "intent": "refund_request",
  "product": "professional",
  "paid_recently": true,
  "urgency": "normal"
}
```

## Prompt 模板

```text
请把用户消息分类成 JSON。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 字段必须包含 intent、product、paid_recently、urgency。
3. intent 只能是 refund_request、pricing_question、technical_issue、other。
4. paid_recently 是 boolean。

用户消息：
{message}
```

## Pydantic 校验

```python
from typing import Literal
from pydantic import BaseModel, ValidationError

class TicketIntent(BaseModel):
    intent: Literal["refund_request", "pricing_question", "technical_issue", "other"]
    product: str | None
    paid_recently: bool
    urgency: Literal["low", "normal", "high"]

try:
    parsed = TicketIntent.model_validate_json(model_output)
except ValidationError as exc:
    print("模型输出不符合结构", exc)
```

## 失败处理

常见失败：

- 输出 Markdown 包裹 JSON。
- 少字段。
- 字段类型错。
- 枚举值不在允许范围内。
- 额外解释文字混在 JSON 后面。

处理策略：

1. 第一次 prompt 写清结构。
2. 解析失败时，把错误信息发回模型要求修复。
3. 设置最大重试次数。
4. 仍失败时返回人工兜底或默认分类。

修复 prompt：

```text
上一次输出无法解析为目标 JSON。

错误信息：
{validation_error}

请只输出修复后的 JSON，不要解释。
```

## 与 Tool Calling 的区别

| 场景 | 结构化输出 | Tool Calling |
| --- | --- | --- |
| 想拿到一个 JSON 结果 | 适合 | 不一定需要 |
| 要执行外部函数 | 不适合 | 适合 |
| 分类、抽取、评分 | 适合 | 通常不需要 |
| 查天气、发邮件、查数据库 | 不适合 | 适合 |

## 常见错误

- 只在 prompt 里说“输出 JSON”，但不校验。
- 让模型自由决定字段名。
- 解析失败后直接崩溃。
- 对开放式解释任务强行套复杂 schema。

## 练习

设计一个客服工单分类 schema，字段包含：

- `intent`
- `product`
- `sentiment`
- `needs_human`
- `summary`

写出 prompt 和 Pydantic 模型，并说明解析失败时如何重试。
