# 06 LLM 基础概念

前面几章解释了 Transformer 如何把 token 序列变成下一个 token 的概率分布。
这一章把模型内部原理和 API 使用之间的概念接起来。

## 本章要点

- LLM API 调用的输入最终都会变成 token 序列。
- Chat model、base model、instruct model 是不同训练和对齐阶段的结果。
- context window 决定一次请求能放多少输入和输出。
- embedding model 和 chat model 不是一类模型，不能混用。
- temperature、top_p、max_tokens 是控制生成行为的常用参数。

## 从 Transformer 到 Chat API

聊天 API 看起来是结构化消息：

```json
[
  {"role": "system", "content": "你是客服助手"},
  {"role": "user", "content": "会员能退款吗？"}
]
```

但模型真正看到的是序列化后的 token：

```text
<system> 你是客服助手 </system>
<user> 会员能退款吗？ </user>
<assistant>
```

然后 Decoder-only 模型从 `<assistant>` 后面开始预测下一个 token，直到生成完整回答或达到停止条件。

## 三类模型

| 类型 | 作用 | 例子 |
| --- | --- | --- |
| Base model | 主要学会续写文本 | 给一段话，继续写下去 |
| Instruct model | 学会遵循指令 | “把下面内容总结成 3 点” |
| Chat model | 学会多轮对话和角色消息 | system/user/assistant 消息 |

现代 API 里常用的是 chat/instruct 模型。它们并不是只会“聊天”，而是更适合按照用户指令完成任务。

## Context Window

context window 是一次请求中模型能处理的 token 上限。

```text
system prompt
+ 用户问题
+ 历史消息
+ RAG 检索内容
+ 工具返回结果
+ 模型输出
<= context window
```

如果窗口是 8k token，不代表你可以塞 8k token 输入后还让模型输出 2k token。输入和输出共享窗口预算。

工程启发：

- 多轮对话要裁剪历史。
- RAG 要检索 Top-K，而不是塞入全部文档。
- 工具结果要摘要。
- 长文本任务要分块处理。

## Chat Model vs Embedding Model

| 模型 | 输入 | 输出 | 用途 |
| --- | --- | --- | --- |
| Chat model | 消息或文本 | 文本 token | 对话、总结、抽取、工具调用 |
| Embedding model | 文本 | 向量 | 语义搜索、相似度、RAG 检索 |

不要用 chat model 做向量检索，也不要期待 embedding model 生成自然语言回答。

## 生成参数直觉

### `max_tokens`

控制最多生成多少 token。

太小：回答被截断。  
太大：成本失控，模型可能啰嗦。

### `temperature`

控制采样随机性。

| 值 | 直觉 | 适合 |
| --- | --- | --- |
| 低 | 稳定、保守 | JSON、分类、抽取、代码修复 |
| 高 | 多样、发散 | 创意写作、脑暴 |

### `top_p`

从累计概率最高的一批 token 中采样。通常不需要同时大幅调整 `temperature` 和 `top_p`。

## 模型知识和工具知识

模型参数里包含训练期间学到的统计知识，但它：

- 不知道训练后的新事实。
- 不知道你的私有数据。
- 不能直接访问数据库。
- 不能真正执行外部动作。

工程上用三类办法补足：

| 缺口 | 方案 |
| --- | --- |
| 不知道私有文档 | RAG |
| 需要实时数据 | Tool calling / MCP |
| 需要长期状态 | Memory / 数据库 |

## 常见误解

**误解：模型“记住了”上次对话。**

API 模型默认没有跨请求记忆。你看到的多轮效果，是应用把历史消息再次传给模型。

**误解：上下文越长越好。**

长上下文会增加成本和干扰。更好的做法是筛选相关信息。

**误解：强模型可以代替权限系统。**

不能。权限、审计、审批必须在应用侧实现。

## 练习

解释下面几个配置分别影响什么：

```text
MODEL_NAME=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
max_tokens=500
temperature=0.2
```

再思考：为什么 RAG 应用通常至少需要一个 chat model 和一个 embedding model？
