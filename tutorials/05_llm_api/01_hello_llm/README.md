# 01 第一次调用：Hello LLM

调一次大模型，本质上就是一次 HTTP 请求：把"消息列表"发过去，把"回答"收回来。
本章用 4 个小演示走完这条最短路径，并拆开响应对象看看里面都有什么。

## 本章要点

- **一次调用**：`client.chat.completions.create(model=..., messages=[...])`，
  回答取 `response.choices[0].message.content`。
- **三种消息角色**：
  - `system`：人设与规矩，优先级最高，用户看不到；
  - `user`：用户的输入；
  - `assistant`：模型的历史回答，多轮对话时原样放回列表模型才"记得"。
- **响应不止文本**：`finish_reason`（`stop` 正常结束 / `length` 被截断）、
  `usage`（输入/输出 token 数，计费依据）。
- **system prompt**：同一份知识，换人设就换回答风格——成本为零，效果立竿见影。

## 运行

需要先配好 `.env`（见[模块首页](../README.md#环境准备)），然后在仓库根目录：

```bash
uv run tutorials/05_llm_api/01_hello_llm/main.py
```

## 核心概念

- **无状态的 API**：每次请求互相独立，服务器不保存任何上下文。想让模型"记得"，
  只能把历史消息一起发过去（第 3 章的主题）。
- **token**：模型读写文本的最小计费单位，大致 1 个汉字 ≈ 1~2 token、1 个英文单词 ≈ 1 token。
  输入（prompt）和输出（completion）分别计价，输出通常贵好几倍。
- **choices 为什么是个列表**：API 支持一次返回多个候选回答（参数 `n`），
  日常几乎不用，所以固定取 `[0]` 即可。

## 常见错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `AuthenticationError` (401) | 密钥没配 / 复制时多了空格 | 检查 `.env` 的 `OPENAI_API_KEY` |
| `NotFoundError` (404) | `OPENAI_BASE_URL` 带了 `/chat/completions` 后缀 | 只保留到 `/v1` |
| `NotFoundError` (404) | 模型名写错，或该服务没有此模型 | 核对 `MODEL_NAME` |
| `AttributeError: 'str' object ...` | 把 `response.choices[0].message` 当成了字符串 | 再取一层 `.content` |

第 5 章会把这些错误集中演示一遍。

## 练习建议

1. 把第 1 节的问题换成"用一句诗介绍杭州"，运行两次，观察回答是否完全相同。
2. 给第 4 节再加一个人设（如"愤世嫉俗的脱口秀演员"），对比三种风格。
3. 故意把 `.env` 里的密钥改错一个字符再运行，记住报错的样子（改回来再跑通）。
