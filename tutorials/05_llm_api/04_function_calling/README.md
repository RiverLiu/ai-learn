# 04 工具调用：让模型操作外部世界

模型训练完知识就冻结了：不知道今天天气，算小数除法也常出错。工具调用（Function
Calling）给它接上"手脚"——模型负责判断**何时调、调什么**，我们的代码负责**真正执行**。

## 本章要点

- **工具 = JSON Schema 描述 + 本地函数**：模型只看到 `tools` 里的名字/用途/参数
  （看不到实现），`description` 写得越清楚，调用越准。
- **调用循环四步**：模型返回 `tool_calls` → 本地 `json.loads` 参数并执行 →
  结果以 `role="tool"` 消息回传（带 `tool_call_id` 一一对应）→ 再问模型，
  直到它不再要工具、给出最终回答。
- **这是 Agent 的最小骨架**：后面 [mcp 教程](../../12_mcp/)的工具协议、
  [langchain 教程](../../09_langchain/)的 `@tool` 装饰器，全是这套循环的封装。

## 运行

需要先配好 `.env`（见[模块首页](../README.md#环境准备)），然后在仓库根目录：

```bash
uv run tutorials/05_llm_api/04_function_calling/main.py
```

预期输出里能看到 `[第 N 轮] 模型请求工具 get_weather(...)` 这样的中间步骤，
以及模型基于工具结果给出的最终自然语言回答；除零时工具返回错误，模型会如实解释。

## 核心概念

- **模型从不执行工具**：它只输出"我想调 get_weather，参数是 {...}"这段结构化文本。
  执行权永远在你的代码里——这也意味着你可以在执行前做权限校验（生产环境必做）。
- **`tool_call_id` 是配对关键**：一次可能返回多个 `tool_calls`，每条 tool 消息靠
  `tool_call_id` 对应到具体请求，配错或漏回会直接报错。
- **工具错误也是数据**：除零、查不到城市时返回 `{"错误": ...}` 即可，模型会理解
  并转述给用户，不需要抛异常。
- **假数据无碍学习**：本章工具返回固定数据，把 `get_weather` 内部换成真实 HTTP
  请求（回顾 [basic 模块](../../02_basic/)的 aiohttp）就是生产级天气助手。

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `JSONDecodeError` | 忘了 `tool_calls` 的参数是 JSON 字符串 | `json.loads(call.function.arguments)` |
| 报"tool_call_id 未对应" | tool 消息缺 `tool_call_id` 或和请求不匹配 | 原样回填 `call.id` |
| 模型死活不调工具 | 问题不明确，或 schema 的 description 太含糊 | 明确要求 + 写清工具用途 |
| 死循环 | 模型反复要求调工具 | 循环设上限，超上限兜底退出 |
| `TypeError: ... argument` | 模型给的参数名/类型与函数签名不符 | schema 的 properties 与函数参数严格对齐 |

## 练习建议

1. 新增一个工具 `get_time(timezone)`（返回固定时间），问"北京现在几点"，观察循环。
2. 把 `get_weather` 的内部换成 aiohttp/httpx 请求一个真实天气 API，对比体验。
3. 在 `FUNCTION_MAP[call.function.name]` 前加一行校验：模型请求不存在的工具名时
   打印警告并回传 `{"错误": "工具不存在"}`，验证模型能否"自我纠正"。
