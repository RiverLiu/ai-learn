# 01 AI 应用架构设计

基础教程已经讲了各个零件：LLM API、Prompt、RAG、Agent、FastAPI、MCP、评估和安全。
本章关注更高一层的问题：这些零件如何组成一个可维护的 AI 应用。

## 本章要点

- AI 应用不是“一个 prompt + 一个接口”，而是一条多层数据流。
- 架构设计的核心是分层、边界、状态和失败处理。
- RAG、Agent、Memory、Tool、MCP、Evaluation 应该放在不同职责层里。
- 生产应用必须把“模型不确定性”当作正常情况处理。

## 推荐分层

```text
┌────────────────────────────────────────────┐
│ 用户入口层：Web / API / Chat UI / App       │
├────────────────────────────────────────────┤
│ 应用服务层：鉴权、租户、会话、限流、任务状态 │
├────────────────────────────────────────────┤
│ AI 编排层：Prompt、Agent、Graph、工具审批    │
├────────────────────────────────────────────┤
│ 能力层：LLM、Embedding、Rerank、ASR、Vision  │
├────────────────────────────────────────────┤
│ 知识层：文档、切块、向量库、元数据、索引      │
├────────────────────────────────────────────┤
│ 状态层：数据库、缓存、对象存储、消息队列      │
├────────────────────────────────────────────┤
│ 运维层：日志、Trace、评估、告警、部署         │
└────────────────────────────────────────────┘
```

这个分层不是为了画图好看，而是为了避免三个常见问题：

- 业务代码直接拼 prompt，后期无法测试和复用。
- RAG、Agent、鉴权、日志混在同一个函数里，任何改动都影响全链路。
- 出错时不知道是检索失败、模型失败、工具失败还是前端展示失败。

## 核心模块边界

| 模块 | 负责什么 | 不应该负责什么 |
| --- | --- | --- |
| API Router | 请求校验、鉴权入口、返回协议 | 拼 prompt、直接访问向量库 |
| Application Service | 编排业务流程、事务边界、租户隔离 | 具体模型调用细节 |
| AI Orchestrator | Prompt、工具调用、Agent 状态机 | 用户权限和数据库事务 |
| Retriever | 查询改写、召回、rerank、引用整理 | 生成最终回答 |
| Tool Adapter | 外部系统调用、参数校验、错误转换 | 决定业务策略 |
| Evaluation | 样本、指标、回归测试 | 在线用户请求主流程 |
| Observability | trace、日志、成本、失败样本 | 修改业务结果 |

## 请求链路示例

以“知识库客服问答”为例：

```text
POST /chat
  ↓
鉴权和租户识别
  ↓
读取会话历史
  ↓
问题改写和意图判断
  ↓
知识库检索 + rerank
  ↓
组装 prompt
  ↓
调用模型流式生成
  ↓
保存回答、引用、token 成本
  ↓
前端展示答案和来源
```

如果用户问题需要调用工具：

```text
模型提出 tool call
  ↓
校验工具权限
  ↓
高风险操作请求人工确认
  ↓
执行工具
  ↓
把工具结果写回上下文
  ↓
模型生成最终答复
```

## 架构决策清单

### 是否需要 Agent

不需要 Agent 的场景：

- 单轮问答
- 固定 RAG
- 固定格式抽取
- 明确的一步工具调用

需要 Agent 的场景：

- 需要多步规划
- 需要根据中间结果选择工具
- 需要读写多个文件或系统
- 任务可能持续几十秒到几分钟

判断标准：如果流程可以画成固定 DAG，优先用普通编排；如果下一步依赖模型判断和工具结果，再考虑 Agent。

### 是否需要 Memory

短期记忆适合：

- 多轮对话
- 上下文澄清
- 同一任务内的状态跟踪

长期记忆适合：

- 用户偏好
- 组织规则
- 历史事实
- 可复用的工作上下文

不要把所有历史都塞进 prompt。长期记忆要有抽取、存储、召回和过期策略。

### 是否需要 MCP

MCP 适合工具和数据源需要被多个 AI 客户端复用的场景。

如果只是一个后端内部函数，普通 tool calling 更简单；如果要让 Claude Desktop、Codex、内部 Agent 平台都能接同一套工具，MCP 更合适。

## 常见架构坏味道

- 一个 `chat()` 函数里完成鉴权、RAG、prompt、模型调用、日志和数据库写入。
- 每个接口都重新拼一套 prompt，没有集中管理。
- 没有 trace id，线上报错只能看用户截图。
- RAG 只存 chunk 文本，不存文档来源、版本、权限和更新时间。
- 工具调用没有权限模型，模型想调什么就调什么。
- 评估脚本和线上代码完全脱节，评估结果不能解释线上问题。

## 具体示例：把一个聊天接口拆成 4 层

很多初学者会把聊天接口写成这样：

```python
@app.post("/chat")
def chat(req: ChatRequest):
    docs = vector_search(req.message)
    prompt = f"根据资料回答：{docs}\n用户问题：{req.message}"
    answer = client.chat.completions.create(...)
    save_to_db(req.user_id, req.message, answer)
    return {"answer": answer}
```

这个版本能跑，但后续很难加权限、日志、评估和工具调用。更好的拆法：

```text
api/chat.py
  只处理 HTTP、鉴权、请求响应模型

services/chat_service.py
  处理会话、业务流程、数据库事务

retrieval/knowledge_base.py
  处理 query rewrite、权限过滤、向量检索、rerank

ai/chat_orchestrator.py
  处理 prompt、模型调用、工具调用、流式输出
```

调用关系：

```python
@router.post("/chat")
async def chat(req: ChatRequest, user: CurrentUser):
    return await chat_service.reply(user=user, message=req.message)
```

`chat_service.reply()` 内部再调用：

```python
docs = await knowledge_base.retrieve(
    query=message,
    tenant_id=user.tenant_id,
    permission_groups=user.groups,
)
stream = ai_orchestrator.answer(message=message, documents=docs)
```

这样做的好处是：检索策略可以单独测试，Prompt 可以单独版本化，API 层不用知道向量库细节，后续加 trace 和成本统计也有明确位置。

## 实践任务

基于 [tutorials/capstone](../../tutorials/capstone/) 画出当前架构，并标出：

- API 层在哪里。
- RAG 检索在哪里。
- Agent 编排在哪里。
- 配置在哪里。
- 哪些地方缺少持久化。
- 哪些地方缺少观测。

然后设计一个改造方案，把当前代码拆成：

- `app/api/`
- `app/services/`
- `app/ai/`
- `app/retrieval/`
- `app/db/`
- `app/observability/`
