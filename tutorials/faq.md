# 踩坑 FAQ

本教程全部示例都真实运行过，这一页沉淀学员（和作者）真实踩过的坑。
遇到问题时先在这里检索关键词；每条条目都给出**现象 → 原因 → 解法**。

## 环境与密钥

**`openai.BadRequestError: 400 - url error, please check url`（阿里云 DashScope）**
原因：`OPENAI_BASE_URL` 多写了路径后缀（如 `.../compatible-mode/v1/embeddings`），
SDK 会自动再拼一次 `/embeddings`，实际请求打到 `.../embeddings/embeddings`。
解法：`OPENAI_BASE_URL` **只到 `/v1` 为止**，接口路径由 SDK 拼接。

**修改 `.env` 后"不生效"**
两种常见情况：① 已 `export` 的同名环境变量优先级高于 `.env`（dotenv 不覆盖已有变量），
`unset` 后再试；② 编辑器里开着旧缓冲区，保存时把修复覆盖回去了——改完先 `cat` 确认文件内容。

**Kimi Code 的登录态不能当 API Key 用**
`~/.kimi/credentials/` 里的 OAuth access token 拿去调 `api.kimi.com` 会 401
（且 15 分钟过期）。第三方脚本请在 Kimi Code 控制台创建正式 API Key。

**这个服务怎么没有 embeddings？**
Kimi Code 端点、DeepSeek 等只提供聊天接口，没有 `/v1/embeddings`。
向量模型可选：阿里百炼（text-embedding-v4）、智谱（embedding-3）、
硅基流动（BAAI/bge-m3 等）、火山引擎（doubao-embedding）、本地 Ollama（bge-m3）。

**`uv add` 报 `tls handshake eof`**
网络问题，换镜像：`UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uv add <包>`。

## LLM 调用

**模型"没有记忆"：第二次调用忘了第一次说的名字**
不是 bug。LLM 每次调用都是独立的，记忆 = 把历史消息一起发给模型
（见 `tutorials/llm_api/03_conversation` 与 `tutorials/memory/`）。

**流式输出是空的 / 回答被截断**
检查 `max_tokens` 是否太小（思考型模型的推理过程也消耗输出 token）。

## MCP

**自己写的 stdio Server 一连就挂/报 JSON 解析错**
stdio 传输规定 stdout 一行一条 JSON-RPC 消息。**Server 里任何 `print` 到 stdout 的输出
都会污染协议流**——日志一律走 stderr 或 logging。

**`mcp dev` 报 `typer is required`**
CLI 功能需要 extra：`uv add 'mcp[cli]'`。

**杀不掉 `uv run` 起的服务器（端口还被占用）**
`uv run` 是包装进程，杀掉它不会带走子进程。用端口杀：
`lsof -ti :8000 | xargs kill`。

## FastAPI

**`/docs` 里多出必选的 `args`、`kwargs` 参数**
依赖写成了 `Depends(已含Depends的Annotated别名)`——重复包装导致 FastAPI 拿到的
签名退化为 `(*args, **kwargs)`。别名直接当类型标注用：`db: db_session`。

**Swagger UI 多文件上传没有"添加第二个文件"按钮**
选择框本身支持多选：在系统文件对话框里 `Cmd/Ctrl` 点选多个文件一起上传。
只能单选时是浏览器缓存了旧版 swagger-ui，`Cmd+Shift+R` 强刷。

## RAG / 向量

**检索结果全是错的 / 分数都一样**
换了 embedding 模型但索引是旧模型建的——**索引与查询必须用同一个 embedding 模型**，
换模型必须重建索引。

**向量维度对不上报错**
同一个向量库混入了不同模型的向量（维度不同）。清空索引，统一模型后重建。
