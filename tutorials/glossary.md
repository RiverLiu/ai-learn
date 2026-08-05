# AI 开发术语表

按主题分组，中英对照 + 一句话解释。遇到生词先查这里。

## 模型基础

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 大语言模型 | LLM (Large Language Model) | 用海量文本训练、以"预测下一个词"方式工作的模型，如 GPT、Kimi、Qwen |
| 词元 | Token | 模型处理文本的最小单位，约 0.5-1 个汉字；计费与上下文长度都按它算 |
| 上下文窗口 | Context Window | 模型一次能"看到"的最大 token 数，超出部分被截断遗忘 |
| 温度 | Temperature | 采样随机度：0 接近确定答案，越大越发散 |
| 系统提示词 | System Prompt | 设定模型角色与行为边界的消息，优先级最高 |
| 幻觉 | Hallucination | 模型编造看似合理但不真实的内容 |
| 推理模型 | Reasoning Model | 回答前先在内部"打草稿"（思维链）的模型，如 o 系列、K 系列 |
| 微调 | Fine-tuning | 用自有数据继续训练模型，改变其知识/风格（对比：RAG 不改模型） |

## RAG 与向量

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 向量嵌入 | Embedding | 把文本映射为高维向量，语义相近则向量距离近 |
| 余弦相似度 | Cosine Similarity | 衡量两向量方向夹角，[-1,1] 越接近 1 越相似 |
| 检索增强生成 | RAG (Retrieval-Augmented Generation) | 先检索相关资料再让模型基于它回答的架构 |
| 切块 | Chunking | 把长文档切成适合检索的小块，质量直接决定检索质量 |
| 向量数据库 | Vector Database | 存储向量并支持"找最相似 K 个"的数据库（Chroma/Qdrant/pgvector 等） |
| 召回 | Recall | 检索环节找回相关内容的数量/比例 |
| 重排序 | Rerank | 初检后用更强的模型精排，提升 Top-K 质量 |
| 混合检索 | Hybrid Search | 向量检索 + 关键词检索（BM25）结合 |

## Agent 与工具

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 智能体 | Agent | "LLM 决策 → 调工具 → 看结果 → 再决策"循环驱动的程序 |
| 工具调用 | Tool/Function Calling | 模型按约定格式表达"想调哪个函数、传什么参"，由程序执行 |
| 模型上下文协议 | MCP (Model Context Protocol) | 标准化"工具/数据源 ↔ AI 应用"连接的开放协议 |
| 反应式代理 | ReAct (Reason+Act) | 边推理边行动的经典 Agent 范式 |
| 子代理 | Sub-agent | 被主代理派单、拥有独立上下文的代理 |
| 人机协作 | Human-in-the-loop | 关键动作暂停等人审批再继续的机制 |
| 检查点 | Checkpointer | LangGraph 中保存/恢复图执行状态的组件（短期记忆） |
| 深度代理 | Deep Agent | 具备规划、文件系统、子代理能力的长任务代理 |

## 工程化

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 追踪 | Tracing | 记录每次链/模型/工具调用的输入输出与耗时（LangSmith 等） |
| 评估 | Evaluation | 用评估集与指标客观衡量 AI 应用效果，替代"凭感觉调参" |
| LLM 裁判 | LLM-as-judge | 用强模型给输出打分的评估方法 |
| 提示词注入 | Prompt Injection | 恶意输入劫持模型行为的安全攻击 |
| 服务器推送事件 | SSE (Server-Sent Events) | 服务器向浏览器单向推送的协议，AI 打字机输出的标配 |
| 语义缓存 | Semantic Cache | 对相似问题直接命中缓存答案，省 token |
| 令牌限流 | Rate Limit | API 的调用频率限制（触发 429），需退避重试 |

## 框架协议速查

| 名词 | 一句话定位 |
| --- | --- |
| LangChain | LLM 组件库 + LCEL 编排语言 |
| LangGraph | Agent 编排框架：状态图、循环、持久化 |
| LangSmith | LangChain 生态的观测与评估平台 |
| Deep Agents | 基于 LangGraph 的预建深度代理框架 |
| FastAPI | 现代 Python Web 框架（本教程用它做 AI 应用后端） |
| Ollama | 本地运行开源模型的工具，提供 OpenAI 兼容端点 |
