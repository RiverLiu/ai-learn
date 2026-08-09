# 10 生产级毕业项目

[tutorials/20_capstone](../../tutorials/20_capstone/) 已经把 RAG、Agent、SSE 和评估串成了一个可运行项目。
本章给出升级路线，把它从教学 demo 推向生产级 AI 应用。

## 升级目标

升级后的项目应具备：

- 用户登录和租户隔离。
- 知识库上传、解析、索引和删除。
- 后台任务处理长流程。
- 对话历史持久化。
- RAG 引用和来源展示。
- 用户反馈和失败样本回流。
- 离线评估和 CI 回归。
- 成本、日志、trace 和基础监控。
- Docker Compose 一键启动。

## 当前基础能力

Capstone 已覆盖：

- FastAPI 服务。
- RAG 知识库。
- Agent 回答。
- SSE 流式输出。
- 基础评估脚本。

缺口：

- 没有用户系统。
- 知识库文件是静态目录。
- 没有后台索引任务。
- 对话和反馈没有完整持久化。
- 缺少前端管理界面。
- 缺少部署编排。
- 缺少线上观测闭环。

## 推荐迭代路线

### 第 1 阶段：项目结构升级

目标：拆清模块边界。

```text
app/
├── api/
├── services/
├── ai/
├── retrieval/
├── db/
├── tasks/
├── schemas/
└── observability/
```

交付：

- API 层不直接拼 prompt。
- RAG 检索封装成独立服务。
- 模型调用封装成独立 adapter。
- 配置集中管理。

### 第 2 阶段：数据持久化

增加数据库表：

- `users`
- `conversations`
- `messages`
- `documents`
- `chunks`
- `index_tasks`
- `feedback`
- `llm_calls`

交付：

- 对话刷新后不丢。
- 文档状态可查询。
- 用户反馈可追踪。

### 第 3 阶段：知识库管理

功能：

- 上传文档。
- 后台解析。
- 切块和 embedding。
- 索引状态展示。
- 删除文档时删除对应 chunk。
- 文档版本更新。

交付：

- 用户可以自己维护知识库。
- RAG 只检索 active 文档。

### 第 4 阶段：前端产品化

页面：

- 登录页。
- Chat 页面。
- 知识库管理页。
- 任务状态页。
- 反馈管理页。

Chat 页面展示：

- 流式回答。
- 引用来源。
- 工具调用状态。
- 重新生成。
- 点赞/点踩。

### 第 5 阶段：评估和观测

能力：

- 线上失败样本进入评估集。
- 每次发布跑小评估集。
- 每天跑完整评估集。
- 记录 token 成本和延迟。
- trace 串联检索、模型、工具调用。

交付：

- 改 prompt 前后能比较分数。
- 线上差评能复现。
- 成本上涨能定位原因。

### 第 6 阶段：部署

组件：

- `api`
- `worker`
- `postgres`
- `redis`
- `vector-db`
- `nginx`

交付：

- `docker compose up` 能启动完整本地环境。
- staging 和 production 使用不同配置。
- 提供健康检查和回滚方案。

## 验收标准

一个升级后的毕业项目，至少要能通过这些验收：

- 新用户可以登录并创建对话。
- 用户上传文档后能看到索引进度。
- 文档索引完成后，问答能引用该文档。
- 删除文档后，答案不再引用它。
- 点踩反馈能在后台看到 trace。
- CI 能跑单元测试和小评估集。
- Docker Compose 能启动 API、Worker、数据库、缓存和向量库。
- 日志能看到每次请求的模型、token、延迟和 trace id。

## 具体示例：一次完整用户旅程

升级后的 Capstone 应支持这样的流程：

```text
1. 用户登录
2. 上传 pricing.md
3. 系统创建索引任务 task_001
4. 前端显示“解析中 → 生成向量 → 已完成”
5. 用户提问：企业版支持什么？
6. 系统检索 pricing.md，生成带引用回答
7. 用户点踩：少说了专属客户成功经理
8. 后台保存 feedback，并关联 trace_id
9. 运营把这条反馈加入评估集
10. 下一次改 prompt 时，CI 自动检查该问题是否已修复
```

对应数据流：

```text
documents
  doc_001 pricing.md active

index_tasks
  task_001 doc_001 succeeded

conversations
  conv_001 user_001

messages
  msg_user_001: 企业版支持什么？
  msg_ai_001: 企业版支持...

retrieval_events
  msg_ai_001 → pricing.md#企业版

feedback
  msg_ai_001 rating=down comment=少说了专属客户成功经理
```

对应验收问题：

```text
删除 pricing.md 后，再问“企业版支持什么？”，系统不能继续引用已删除文档。
```

这个旅程把高级教程里的数据管道、RAG、前端、后台任务、可观测性和测试全部串起来。

## 练习

把升级拆成 4 个里程碑：

1. 数据库和项目结构。
2. 知识库上传和后台索引。
3. 前端 Chat 和引用展示。
4. 评估、观测和部署。

每个里程碑都要求：

- 有可运行代码。
- 有 README。
- 有至少一个测试。
- 有明确的验收命令。
