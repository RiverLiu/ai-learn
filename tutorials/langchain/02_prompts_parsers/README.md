# 02 提示词模板与输出解析

模型调用的两端各有一个"脏活"：输入侧拼提示词，输出侧解析文本。LangChain 分别用
**PromptTemplate** 和 **OutputParser / with_structured_output** 解决。

## 本章要点

- `ChatPromptTemplate.from_messages([...])`：用 `("角色", "带{占位符}的内容")` 声明消息模板，
  `.invoke({变量})` 渲染成真正的消息列表——渲染结果可以先打印检查，不必盲调模型。
- `StrOutputParser`：把 `AIMessage` 转成纯字符串，链条下游直接拿到文本。
- `with_structured_output(Pydantic模型)`：声明返回结构，模型输出被自动解析校验成
  **Pydantic 对象**（字段类型、`Field(description=...)` 会进入给模型的 schema）。
- `prompt | model | parser` 这条管道就是 LCEL，第 3 章专门展开。

## 运行

```bash
uv run tutorials/langchain/02_prompts_parsers/main.py
```

预期输出：先打印翻译模板的渲染结果与译文，再打印解析好的 `Recipe` 对象字段。

## 核心概念

- **结构化输出优先于正则解析**：现代模型原生支持按 JSON Schema 输出，
  不要再手写"请用 JSON 回答"+ `json.loads` + try/except。
- **description 即提示词**：Pydantic 字段的 `description` 会传给模型，写得越清楚输出越准。
