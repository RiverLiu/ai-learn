"""结构化输出的离线校验示例。

真实项目里，JSON 字符串来自 LLM 输出；本章为了稳定演示，使用几段模拟输出：
- 一段合法 JSON
- 一段 Markdown 包裹的 JSON
- 一段字段缺失/枚举错误的 JSON

运行：
    uv run tutorials/05_llm_api/07_structured_outputs/main.py
"""

import json
import re
from typing import Literal

from pydantic import BaseModel, ValidationError


class TicketIntent(BaseModel):
    intent: Literal["refund_request", "pricing_question", "technical_issue", "other"]
    product: str | None
    paid_recently: bool
    urgency: Literal["low", "normal", "high"]
    summary: str


MODEL_OUTPUTS = [
    """
{
  "intent": "refund_request",
  "product": "professional",
  "paid_recently": true,
  "urgency": "normal",
  "summary": "用户刚购买专业版后咨询退款"
}
""",
    """
```json
{
  "intent": "pricing_question",
  "product": "enterprise",
  "paid_recently": false,
  "urgency": "low",
  "summary": "用户咨询企业版价格"
}
```
""",
    """
{
  "intent": "refund",
  "product": "professional",
  "urgency": "urgent",
  "summary": "用户要求退款"
}
""",
]


def extract_json(text: str) -> str:
    """从模型输出中提取 JSON 对象文本，兼容 Markdown 代码块。"""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        return fenced.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("输出中没有 JSON 对象")
    return text[start : end + 1]


def parse_ticket_intent(text: str) -> TicketIntent:
    json_text = extract_json(text)
    # 先用 json.loads 给出更清楚的 JSON 语法错误，再交给 Pydantic 校验字段。
    data = json.loads(json_text)
    return TicketIntent.model_validate(data)


def main() -> None:
    for index, output in enumerate(MODEL_OUTPUTS, start=1):
        print(f"\n===== 示例 {index} =====")
        try:
            parsed = parse_ticket_intent(output)
        except (ValueError, json.JSONDecodeError, ValidationError) as exc:
            print("解析失败：")
            print(exc)
            print("处理建议：把错误信息发回模型，请它只输出修复后的 JSON。")
            continue

        print("解析成功：")
        print(parsed.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
