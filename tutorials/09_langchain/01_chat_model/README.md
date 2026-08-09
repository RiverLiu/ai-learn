# 01 与聊天模型对话

LangChain 把一切 LLM 交互抽象为 **Chat Model**：输入消息列表，输出 `AIMessage`。

## 本章要点

- **消息类型**：`SystemMessage`（设定行为）/ `HumanMessage`（用户）/ `AIMessage`（模型回复），
  多轮对话就是把消息不断追加进列表。
- **三种调用方式**：
  - `model.invoke(messages)`：一次性拿完整结果；
  - `model.stream(messages)`：逐段流式返回（chunk），聊天界面标配；
  - `model.batch([...])`：并发处理多组输入。
- 返回的 `AIMessage` 不只是文本：还有 `usage_metadata`（token 用量）、`tool_calls`（第 5 章）等。

## 运行

需要配置模型（见[教程首页](../README.md#模型配置)）：

```bash
uv run tutorials/09_langchain/01_chat_model/main.py
```

## 核心概念

- **统一的模型接口**：`ChatOpenAI`、`ChatAnthropic`、`ChatOllama`……接口完全一致，
  换模型只换构造那一行。本教程用 `ChatOpenAI` 是因为 OpenAI 兼容协议覆盖最广（含国内服务）。
- **AIMessage 是对象不是字符串**：取文本用 `response.content`；想直接要字符串，看下一章的输出解析器。
