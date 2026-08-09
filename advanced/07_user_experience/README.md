# 07 AI 应用前端交互

AI 应用前端不是普通表单页面。它要处理流式输出、长任务状态、文件上传、引用来源、工具调用、人工确认、失败重试和用户反馈。

## 本章要点

- Chat UI 要展示过程，而不是只展示最终答案。
- 流式输出要处理断线、取消、重试和消息补全。
- RAG 应展示引用来源，让用户能验证答案。
- Agent 工具调用需要明确状态和审批交互。

## 常见前端形态

| 产品形态 | 核心交互 |
| --- | --- |
| Chatbot | 多轮对话、流式输出、引用 |
| 知识库问答 | 文件上传、来源引用、反馈 |
| Agent 助手 | 工具调用状态、任务进度、确认按钮 |
| 文档生成 | 大纲、局部编辑、版本对比 |
| 数据分析 | 文件上传、图表、代码执行状态 |

## Chat UI 状态模型

推荐消息状态：

```text
pending → streaming → completed
       ↘ failed
       ↘ cancelled
```

每条 assistant 消息建议包含：

- `message_id`
- `status`
- `content`
- `citations`
- `tool_calls`
- `created_at`
- `completed_at`
- `error`

## SSE 与 WebSocket

SSE 适合：

- 服务端向客户端单向推送。
- ChatGPT 类流式文本。
- 实现简单，HTTP 友好。

WebSocket 适合：

- 双向实时交互。
- 多人协作。
- 需要客户端频繁发送控制消息。

对大多数问答应用，SSE 足够。

## 流式事件设计

不要只传文本片段。建议传结构化事件：

```json
{"type": "message_start", "message_id": "m_001"}
{"type": "token", "delta": "你好"}
{"type": "retrieval", "documents": [{"title": "FAQ", "score": 0.82}]}
{"type": "tool_call", "name": "search_docs", "status": "running"}
{"type": "tool_result", "name": "search_docs", "status": "completed"}
{"type": "message_end"}
```

这样前端可以展示：

- 正在检索
- 正在调用工具
- 正在生成
- 已完成
- 失败原因

## 引用展示

RAG 答案应展示来源：

- 文档标题
- 章节
- 页码
- 更新时间
- 原文片段
- 点击打开来源

避免只写“根据知识库”。用户需要知道答案来自哪里。

## 文件上传

文件上传流程：

```text
选择文件
  ↓
上传到对象存储或后端
  ↓
创建文档记录
  ↓
后台解析和索引
  ↓
前端轮询或订阅索引状态
  ↓
可问答
```

前端应展示：

- 上传进度
- 解析状态
- 索引状态
- 失败原因
- 可删除/重试

## 人机确认

高风险工具调用前需要确认：

```text
Agent 想执行：发送邮件给客户
收件人：...
主题：...
正文摘要：...
[确认发送] [修改] [取消]
```

确认页要展示模型将要执行的具体动作，而不是只问“是否允许工具调用”。

## 常见坑

- 流式输出失败后消息卡在“生成中”。
- 页面刷新后丢失会话状态。
- RAG 引用不可点击，用户无法核验。
- 工具调用过程不可见，用户不知道 Agent 在做什么。
- 没有取消按钮，长任务只能等。
- 文件上传成功但索引失败，前端仍显示可用。

## 具体示例：一个带引用的流式回答

服务端 SSE：

```text
event: message
data: {"type":"message_start","message_id":"m_001"}

event: message
data: {"type":"status","text":"正在检索知识库"}

event: message
data: {"type":"citation","id":"c1","title":"FAQ","section":"退款规则","source_uri":"faq.md"}

event: message
data: {"type":"token","delta":"购买后 "}

event: message
data: {"type":"token","delta":"7 天内可以申请退款。"}

event: message
data: {"type":"message_end","message_id":"m_001"}
```

前端状态可以设计成：

```json
{
  "id": "m_001",
  "role": "assistant",
  "status": "streaming",
  "content": "购买后 7 天内可以申请退款。",
  "citations": [
    {
      "id": "c1",
      "title": "FAQ",
      "section": "退款规则",
      "source_uri": "faq.md"
    }
  ]
}
```

界面展示：

```text
购买后 7 天内可以申请退款。 [1]

来源
[1] FAQ / 退款规则 / faq.md
```

这比只显示一段文本更适合生产应用，因为用户可以核验答案，客服也能快速定位依据。

## 实践任务

基于 [tutorials/08_fastapi/13_streaming_sse](../../tutorials/08_fastapi/13_streaming_sse/)：

1. 把 token 事件改成结构化事件。
2. 增加 `message_start`、`retrieval`、`message_end`。
3. 前端展示“检索中 / 生成中 / 完成”。
4. 给回答增加 citations 区域。
5. 增加“停止生成”和“重新生成”按钮设计。
