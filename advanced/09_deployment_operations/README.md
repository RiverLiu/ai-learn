# 09 生产部署与运维

基础教程中的部署通常只需要 `uvicorn` 跑起来。生产部署还需要进程管理、反向代理、HTTPS、数据库、缓存、向量库、配置、日志、健康检查和回滚。

## 本章要点

- AI 应用部署不是只部署一个 FastAPI 服务。
- 最小生产环境通常至少包含 API、数据库、缓存、向量库和对象存储。
- 配置要分环境管理，密钥不能写进代码。
- 健康检查、日志和回滚是上线基本要求。

## 推荐组件

```text
Nginx / Gateway
  ↓
FastAPI API Server
  ↓
Postgres：用户、会话、任务、反馈
Redis：缓存、限流、队列
Vector DB：知识库向量
Object Storage：上传文件、原始文档
Worker：后台解析、embedding、评估
Observability：日志、trace、指标
```

## Docker Compose 开发环境

高级教程建议提供一个本地生产近似环境：

```text
docker-compose.yml
├── api
├── worker
├── postgres
├── redis
├── qdrant
└── nginx
```

这样学习者能理解多服务协作，而不是只在单进程里跑 demo。

## 配置管理

推荐环境变量分类：

```text
APP_ENV=production
DATABASE_URL=...
REDIS_URL=...
VECTOR_DB_URL=...
OBJECT_STORAGE_BUCKET=...
OPENAI_API_KEY=...
OPENAI_BASE_URL=...
MODEL_NAME=...
EMBEDDING_MODEL=...
LOG_LEVEL=INFO
```

原则：

- `.env.example` 提供模板，不包含真实密钥。
- 生产密钥由部署平台或 secret manager 注入。
- 不同环境使用不同数据库和向量库。
- 启动时校验关键配置。

## 健康检查

至少提供：

- `/healthz`：进程是否存活。
- `/readyz`：依赖是否可用。

`readyz` 应检查：

- 数据库连接
- Redis 连接
- 向量库连接
- 模型服务可选检查

模型服务检查可能有成本和延迟，生产中可以只检查配置或使用轻量 ping。

## 发布策略

基础策略：

- 先部署 staging。
- 跑 smoke test。
- 跑小评估集。
- 灰度一部分流量。
- 观察错误率、延迟、成本和点踩率。
- 异常时回滚。

AI 应用还要关注：

- prompt 版本是否一起发布。
- 知识库版本是否兼容。
- 模型版本是否变化。
- 评估集分数是否下降。

## 数据迁移

涉及：

- 数据库 schema migration。
- 向量库 collection 版本。
- embedding 模型变化后的重建索引。
- 文档解析规则变化后的重建。

不要在用户请求路径里做迁移。

## 常见坑

- 本地用 SQLite，生产改 Postgres 后事务和并发问题暴露。
- 向量库没有备份，重建成本高。
- prompt 改动没有版本号，无法回滚。
- 没有 readiness check，服务启动了但依赖不可用。
- 日志只写本地文件，容器重启后丢失。
- Docker 镜像里包含 `.env` 或密钥。

## 具体示例：最小 Docker Compose 形态

一个生产近似的本地环境可以从这几个服务开始：

```yaml
services:
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    env_file: .env
    depends_on:
      - postgres
      - redis
      - qdrant

  worker:
    build: .
    command: python -m app.tasks.worker
    env_file: .env
    depends_on:
      - postgres
      - redis
      - qdrant

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ai_app
      POSTGRES_USER: ai_app
      POSTGRES_PASSWORD: ai_app_dev

  redis:
    image: redis:7

  qdrant:
    image: qdrant/qdrant:latest
```

`.env.example` 应该写成：

```text
DATABASE_URL=postgresql://ai_app:ai_app_dev@postgres:5432/ai_app
REDIS_URL=redis://redis:6379/0
VECTOR_DB_URL=http://qdrant:6333
OPENAI_API_KEY=replace-me
MODEL_NAME=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

注意：这里的密码只适合本地开发。生产环境要由部署平台注入 secret，不要提交真实 `.env`。

## 实践任务

为 [tutorials/capstone](../../tutorials/capstone/) 设计生产部署方案：

1. API 和 Worker 分开部署。
2. Postgres 存会话、任务和反馈。
3. Redis 做队列和缓存。
4. Qdrant 或 pgvector 做向量库。
5. Nginx 处理 HTTPS 和反向代理。
6. 增加 `/healthz` 和 `/readyz`。
7. 写出灰度发布和回滚流程。
