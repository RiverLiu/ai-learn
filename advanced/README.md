# 高级教程

`advanced/` 是 AI 应用开发的高级教程区，面向已经跑通 [基础教程](../tutorials/) 的学习者。
基础教程回答“怎么跑通”；高级教程回答“怎么把 AI 应用长期稳定地跑在生产环境里”。

高级教程不再按单个技术点平铺，而是按**生产 AI 应用生命周期**组织：

```text
产品与架构
  ↓
知识工程
  ↓
生产级 RAG
  ↓
Agent 工程化
  ↓
质量工程
  ↓
观测与成本
  ↓
用户体验
  ↓
异步工作流
  ↓
部署运维
  ↓
生产级毕业项目
```

## 目录

| 顺序 | 模块 | 解决的问题 |
| --- | --- | --- |
| 1 | [01_product_architecture](./01_product_architecture/) | 如何把 demo 拆成可维护的产品架构 |
| 2 | [02_knowledge_engineering](./02_knowledge_engineering/) | 如何把原始文档变成可治理、可更新、可检索的知识库 |
| 3 | [03_production_rag](./03_production_rag/) | 如何提升 RAG 的召回、排序、引用和可靠性 |
| 4 | [04_agent_engineering](./04_agent_engineering/) | 如何把 Agent、Tools、MCP、Skills 做成可控能力 |
| 5 | [05_quality_engineering](./05_quality_engineering/) | 如何测试 LLM 应用、做 prompt 回归和 CI 评估 |
| 6 | [06_observability_cost](./06_observability_cost/) | 如何定位线上问题、收集反馈、控制 token 成本和延迟 |
| 7 | [07_user_experience](./07_user_experience/) | 如何设计 Chat UI、流式输出、引用展示和文件上传体验 |
| 8 | [08_async_workflows](./08_async_workflows/) | 如何处理文档索引、批量 embedding、长任务和队列 |
| 9 | [09_deployment_operations](./09_deployment_operations/) | 如何用 Docker、数据库、缓存、向量库和 Nginx 部署 |
| 10 | [10_production_capstone](./10_production_capstone/) | 如何把基础毕业项目升级为生产级 AI 应用 |

## 与 tutorials 的分工

| 目录 | 定位 | 学习目标 |
| --- | --- | --- |
| [tutorials](../tutorials/) | 基础教程 | 掌握 LLM API、Prompt、RAG、Agent、MCP、FastAPI 等核心概念 |
| `advanced` | 高级教程 | 把基础能力组合成可维护、可观测、可扩展、可上线的 AI 应用 |

## 每章结构

高级章节建议统一包含：

1. 你会遇到的问题
2. 本章目标
3. 最小示例
4. 代码结构或数据结构
5. 核心实现
6. 生产注意事项
7. 常见错误
8. 练习

如果第一次学习，建议先读每章的“具体示例”，再看概念和实践任务。

## 推荐路径

企业知识库路径：

```text
01_product_architecture → 02_knowledge_engineering → 03_production_rag → 06_observability_cost → 09_deployment_operations
```

Agent 办公助手路径：

```text
01_product_architecture → 04_agent_engineering → 05_quality_engineering → 06_observability_cost → 10_production_capstone
```

面向用户的 AI 产品路径：

```text
07_user_experience → 06_observability_cost → 05_quality_engineering → 09_deployment_operations
```

综合项目路径：

```text
01_product_architecture → 02_knowledge_engineering → 03_production_rag → 05_quality_engineering → 06_observability_cost → 08_async_workflows → 09_deployment_operations → 10_production_capstone
```
