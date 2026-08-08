# 03 Prompt 回归

Prompt 是代码的一部分。每次修改 prompt，都可能改变输出格式、事实表达、拒答策略和工具选择。

## 样本结构

```json
{
  "id": "pricing_refund_001",
  "input": "买错会员能退吗？",
  "expected_facts": ["7 天内", "可以申请退款"],
  "forbidden_facts": ["30 天", "无条件退款"],
  "expected_format": "answer_with_citations"
}
```

## 练习

为 Capstone 的客服 prompt 建 10 条回归样本，覆盖退款、套餐、数据保留、无法回答和越权问题。
