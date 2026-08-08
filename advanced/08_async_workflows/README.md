# 08 后台任务与异步工作流

AI 应用中很多任务不适合在 HTTP 请求里同步完成，例如大文件解析、批量 embedding、长报告生成、定时知识库更新。
本章讲后台任务系统。

## 本章要点

- 请求线程不应该承担长任务。
- 后台任务需要状态、进度、取消、重试和幂等。
- 知识库索引通常是队列任务，不是同步接口。
- 长任务要有用户可查询的任务记录。

## 典型任务

- 上传文档后的解析和切块。
- 批量生成 embedding。
- 定时同步第三方知识库。
- 长报告生成。
- 多步 Agent 调研。
- 批量评估。
- 清理过期会话和缓存。

## 架构

```text
API Server
  ↓ 创建任务记录
Queue / Broker
  ↓
Worker
  ↓
数据库 / 向量库 / 对象存储
  ↓
前端轮询或订阅任务状态
```

常见组件：

- Redis + RQ
- Redis + Celery
- Dramatiq
- APScheduler
- FastAPI BackgroundTasks（只适合很轻的任务）

## 任务状态

推荐状态机：

```text
pending → running → succeeded
        ↘ failed
        ↘ cancelled
        ↘ retrying
```

任务表字段：

- `task_id`
- `task_type`
- `status`
- `progress`
- `input_ref`
- `result_ref`
- `error_message`
- `retry_count`
- `created_by`
- `created_at`
- `updated_at`

## 幂等设计

后台任务经常会重试。必须避免重复写入：

- 用文档 hash 判断是否需要重新 embedding。
- 用唯一 `chunk_id` upsert 向量。
- 任务开始前检查当前状态。
- 外部副作用操作要有去重 key。

## 取消任务

取消不是简单杀进程。需要：

- API 把任务标记为 `cancel_requested`。
- Worker 在安全点检查取消标记。
- 已写入的中间结果可清理或标记失效。
- 前端展示“正在取消”和“已取消”。

## 重试策略

可重试：

- 网络超时
- 临时限流
- 向量库连接失败
- 模型服务 5xx

不可重试：

- 文件格式不支持
- 权限不足
- 输入参数非法
- 文档解析后无文本

## 常见坑

- 在上传接口里同步 embedding 大文件，导致请求超时。
- 任务失败没有错误信息，用户只能重新上传。
- 重试后重复插入 chunk，检索结果重复。
- 没有取消能力，长任务失控。
- Worker 和 API 使用不同配置，线上难排查。

## 具体示例：上传文档后的索引任务

用户上传 `pricing.pdf` 后，API 不直接解析和 embedding，而是创建任务：

```json
{
  "task_id": "task_001",
  "task_type": "index_document",
  "status": "pending",
  "document_id": "doc_001",
  "progress": 0
}
```

Worker 执行过程：

```text
pending
  ↓ progress=10  下载原始文件
running
  ↓ progress=30  解析 PDF
running
  ↓ progress=50  切块
running
  ↓ progress=80  生成 embedding 并写入向量库
succeeded
  ↓ progress=100 文档变为 active
```

前端轮询：

```http
GET /tasks/task_001
```

返回：

```json
{
  "task_id": "task_001",
  "status": "running",
  "progress": 50,
  "current_step": "chunking",
  "error_message": null
}
```

如果 PDF 解析失败：

```json
{
  "task_id": "task_001",
  "status": "failed",
  "progress": 30,
  "current_step": "parsing",
  "error_message": "PDF contains scanned pages only; OCR is required"
}
```

这个设计让用户知道任务卡在哪里，也让开发者能重试失败任务。

## 实践任务

为 Capstone 设计知识库索引任务：

1. `POST /documents` 只负责上传和创建任务。
2. Worker 负责解析、切块、embedding、写向量库。
3. `GET /tasks/{task_id}` 返回状态和进度。
4. 任务失败时保存错误信息。
5. 相同文档 hash 重复上传时跳过 embedding。
