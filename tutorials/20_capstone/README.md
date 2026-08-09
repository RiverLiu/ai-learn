# 毕业项目：云雀笔记智能客服

把前面各教程学到的能力串成一个完整的 AI 应用：一个基于私有知识库的
流式问答客服，支持多轮对话、工具调用和退款估算。

用户提问 → Agent 判断要"查资料"还是"算退款" → 检索知识库 / 调用计算工具
→ 流式生成带来源标注的回答 → 同一 `thread_id` 内记住上下文。

## 架构

```
                        ┌──────────────────────────────────────────┐
  curl / 前端           │              FastAPI 服务 (app/main.py)  │
  ────────── POST /chat │  POST /chat ── SSE 流式响应              │
    {thread_id,message} │  GET  /health                            │
                        └──────────────┬───────────────────────────┘
                                       │ stream_mode="messages"
                        ┌──────────────▼───────────────────────────┐
                        │        LangGraph Agent (app/agent.py)     │
                        │  create_agent：LLM ◄──► 工具 的 ReAct 循环 │
                        │  MemorySaver：按 thread_id 存档多轮记忆    │
                        └───┬───────────────┬──────────────────────┘
                            │               │
                ┌───────────▼───┐   ┌───────▼───────────────────────┐
                │ search_       │   │ calc_refund                   │
                │ knowledge()   │   │ （按 pricing.md 退款政策估算） │
                └───────┬───────┘   └───────────────────────────────┘
                        │
        ┌───────────────▼────────────────────────────────┐
        │  内存向量索引 (app/knowledge.py，numpy 手写)     │
        │  data/knowledge_base/*.md → 按标题切块 → 向量   │
        └───────────────┬────────────────────────────────┘
                        │ 兼容 OpenAI 协议
        ┌───────────────▼────────┐   ┌──────────────────────────┐
        │  向量服务 (EMBEDDING_*) │   │  聊天服务 (OPENAI_*)      │
        │  如阿里云百炼           │   │  如月之暗面 Kimi          │
        └────────────────────────┘   └──────────────────────────┘
```

## 能力 ←→ 教程对照表

本项目的每一部分都对应一个前置教程，遇到看不懂的代码可以回去复习：

| 本项目模块 | 用到的能力 | 对应教程 |
| --- | --- | --- |
| `app/knowledge.py` | 切块、向量化、余弦相似度检索 | `tutorials/07_rag/`（尤其 `04_rag_pipeline`） |
| `app/agent.py` | create_agent 构建 ReAct 工具调用循环 | `tutorials/10_langgraph/03_react_agent` |
| `app/agent.py` | checkpointer + thread_id 多轮记忆 | `tutorials/10_langgraph/05_persistence` |
| `app/agent.py` | @tool 工具定义 | `tutorials/09_langchain/`、`tutorials/01_tools/` |
| `app/main.py` | SSE 流式输出 token | `tutorials/05_llm_api/02_params_streaming` |
| `app/main.py` | FastAPI 服务形态 | `tutorials/08_fastapi/` |
| `scripts/eval.py` | 评估集 + LLM 评委打分 | `tutorials/15_evaluation/` |
| `app/config.py` | 环境变量管理密钥 | 各教程 `.env` 惯例 |

## 学习前置检查表

开始 Capstone 前，建议至少确认这些能力已经跑通过：

- `tutorials/05_llm_api/01_hello_llm`：能成功调用聊天模型。
- `tutorials/05_llm_api/06_embeddings_api`：理解聊天模型和向量模型的区别。
- `tutorials/07_rag/04_rag_pipeline`：能跑通知识库检索问答。
- `tutorials/08_fastapi/13_streaming_sse`：理解 SSE 流式输出。
- `tutorials/10_langgraph/03_react_agent`：理解工具调用 Agent。
- `tutorials/15_evaluation/02_llm_judge`：理解 LLM-as-judge 的基本评估方式。

如果启动 Capstone 失败，优先回看：

| 问题 | 回看章节 |
| --- | --- |
| API Key / Base URL 报错 | `tutorials/01_tools/05_env_config.md`、`tutorials/05_llm_api` |
| embedding 接口不可用 | `tutorials/05_llm_api/06_embeddings_api`、`tutorials/07_rag/01_embeddings` |
| 检索结果不准 | `tutorials/07_rag/02_chunking`、`tutorials/07_rag/04_rag_pipeline` |
| 流式输出看不懂 | `tutorials/08_fastapi/13_streaming_sse` |
| Agent 工具调用异常 | `tutorials/05_llm_api/08_tool_safety`、`tutorials/10_langgraph/03_react_agent` |

## 双服务配置：聊天一家、向量一家

国内落地时，聊天模型和向量模型常常不在同一家服务商：比如聊天用
月之暗面 Kimi，向量用阿里云百炼。好在各家接口都兼容 OpenAI 协议，
所以配置分两组（见 `app/config.py`）：

- 聊天：`OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL_NAME`
- 向量：`EMBEDDING_API_KEY` / `EMBEDDING_BASE_URL` / `EMBEDDING_MODEL`

向量服务的凭证**缺省时回落到 `OPENAI_*`**——如果两家合一，只配一组即可。

## 运行

1. 配置密钥（参考 `.env.example`）：

   ```bash
   cp tutorials/20_capstone/.env.example tutorials/20_capstone/.env
   # 编辑 .env 填入真实密钥；也可以像仓库其他教程一样用环境变量注入
   ```

2. 启动服务（在仓库根目录执行）：

   ```bash
   uv run uvicorn tutorials.capstone.app.main:app --port 8312
   ```

3. 健康检查：

   ```bash
   curl http://127.0.0.1:8312/health
   # {"status":"ok","service":"larknote-support"}
   ```

4. 流式问答（`-N` 关闭缓冲，逐段看输出）：

   ```bash
   curl -N -X POST http://127.0.0.1:8312/chat \
     -H 'Content-Type: application/json' \
     -d '{"thread_id":"t1","message":"专业版多少钱？学生有优惠吗"}'
   ```

   SSE 事件类型：`status`（接入）→ `tool`（工具调用结果，如知识库检索）
   → `token`（AI 增量文本，若干条）→ `done`（结束）。

5. 多轮记忆：用**同一个 thread_id** 追问，Agent 记得上文；换 id 即新会话：

   ```bash
   curl -N -X POST http://127.0.0.1:8312/chat \
     -H 'Content-Type: application/json' \
     -d '{"thread_id":"t1","message":"那按年付呢？退款怎么算"}'
   ```

6. 跑小评测（5 条问答 + LLM 评委打分，输出评分表）：

   ```bash
   uv run tutorials/20_capstone/scripts/eval.py
   ```

注意：首次请求 /chat（或首次跑 eval）要调用向量接口构建知识库索引，
需几秒钟；之后索引常驻内存，响应只取决于聊天模型速度。

## 扩展练习

1. **加 MCP 工具**：参考 `tutorials/12_mcp/`，把"查询工单状态"做成 MCP 服务，
   让 Agent 通过 MCP 协议调用，体会与本地 @tool 的差别。
2. **换本地模型**：参考 `tutorials/16_local_models/`，用 Ollama 把向量模型换成
   本地模型，观察 `EMBEDDING_BASE_URL` 指向 `localhost` 后双服务配置的变化。
3. **记忆落盘**：把 `MemorySaver` 换成 `SqliteSaver`（`langgraph-checkpoint-sqlite`），
   重启服务后用同一 thread_id 验证记忆仍在。
4. **长期记忆**：参考 `tutorials/11_memory/`，让 Agent 跨线程记住用户偏好
   （如"我是学生"），并在回答价格问题时主动应用。
5. **流式细化**：在 SSE 中增加"正在调用 xxx 工具"的事件（AI 消息块里的
   `tool_calls` 信息），让前端状态提示更及时。
6. **扩充评测**：在 `scripts/eval.py` 的 EVAL_SET 里加入"知识库没有的问题"，
   考察 Agent 是否编造答案（拒答率也是客服质量指标）。
7. **WebSocket 版本**：参考 `tutorials/08_fastapi/10_websocket`，把 /chat 改成
   WebSocket 双向流，对比 SSE 与 WS 在聊天场景下的取舍。

## 文件说明

```
tutorials/20_capstone/
├── README.md            # 本文件
├── .env.example         # 双服务配置示例（不含真实密钥）
├── app/
│   ├── __init__.py
│   ├── config.py        # 双服务配置：聊天（OPENAI_*）与向量（EMBEDDING_*）
│   ├── knowledge.py     # 知识库加载、切块、内存向量索引
│   ├── agent.py         # LangGraph Agent：检索 + 退款工具，checkpointer 记忆
│   └── main.py          # FastAPI：POST /chat（SSE 流式）、GET /health
├── scripts/
│   └── eval.py          # 小评测：5 条问答 + LLM 打分，输出评分表
└── data/knowledge_base/ # 云雀笔记产品文档（拷贝自 rag 教程）
```
