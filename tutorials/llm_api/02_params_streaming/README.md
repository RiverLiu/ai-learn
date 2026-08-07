# 02 参数与流式输出

同一个接口，几个参数就能让模型表现完全不同。本章看三个最常用的：
`temperature`（随机程度）、`max_tokens`（长度上限）、`stream`（边生成边返回）。

## 本章要点

- **temperature**：范围一般 0~2。`0` = 最确定，同一题多次回答几乎一样；
  `2` = 最发散，适合起名、头脑风暴等创意场景。严肃问答/提取用低值，创意用高值。
- **max_tokens**：回答的"天花板"，超了被硬截断，`finish_reason` 变成 `length`
  （正常结束是 `stop`）。注意思考型模型的推理过程也占这个额度，别给太小。
- **stream=True**：返回值变成迭代器，逐块（chunk）取 `choices[0].delta.content`，
  边收边打印就是聊天界面的"打字机效果"。

## 运行

需要先配好 `.env`（见[模块首页](../README.md#环境准备)），然后在仓库根目录：

```bash
uv run tutorials/llm_api/02_params_streaming/main.py
```

预期：两个 temperature 的店名方案明显不同；截断演示的 `finish_reason` 为 `length`，
输出在某个数字处戛然而止；流式演示逐字蹦出。

## 核心概念

- **temperature 的原理（直觉版）**：模型每步都在给"下一个词"打分，temperature
  决定多大概率选低分词。0 = 永远选最高分（确定性），越大越容易"剑走偏锋"。
- **服务商可能锁定参数**：部分思考型模型由服务商固定 temperature（如只允许 1），
  强行传参会报 400——本章代码演示了"报错就退化为默认值"的兼容写法。
- **流式不等于更快**：总耗时差不多，但**首字延迟**从几秒降到零点几秒，
  用户体验天差地别——所有聊天产品默认流式。
- **delta 与 message**：非流式拿完整 `message.content`；流式每块只给增量
  `delta.content`，且首块/末块可能为空，必须判空。

> OpenAI tokenizer tool: https://platform.openai.com/tokenizer

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 流式输出报 `IndexError` / `TypeError` | 没判空就取 `delta.content` | `if text:` 再打印 |
| 思考型模型输出为空且 `finish_reason=length` | `max_tokens` 太小，推理就烧光了额度 | 调大，或先不限制 |
| 回答被截断却没发现 | 没检查 `finish_reason` | 生产代码里断言其为 `stop` |
| `400 invalid temperature: only 1 is allowed` | 该模型由服务商锁定 temperature | 不传该参数，用模型默认值 |
| temperature 传了 3 | 超出范围 | 一般 0~2，以服务商文档为准 |

## 练习建议

1. 把 temperature 对比改成"翻译题"（如把一句中文译成英文），观察差异是否还明显——
   想想为什么创意题差异大、翻译题差异小。
2. 给流式演示加上计时：分别统计"首字出现时间"和"总耗时"，与非流式对比。
3. 把 `max_tokens` 从 100 逐步调大（250、500、1000），观察输出从"空"到"半截"到
   "完整"的过程，理解思考型模型的 token 消耗结构。
