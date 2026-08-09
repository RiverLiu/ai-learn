# 第一次调用 LLM API

前面模块里的"AI"还都是本地代码；从本模块开始，程序要真正连上一个大模型了。
我们直接用官方的 `openai` Python SDK 调用 **Chat Completions 接口**——这是所有
LLM 应用的地基：后面学的 RAG、LangChain、Agent，拆到底层都是这里的一次次 HTTP 请求。

之所以用 `openai` SDK 而不是某个厂商的私有 SDK：国内主流服务（Kimi、DeepSeek、
通义等）都提供 **OpenAI 兼容协议**，学会这一套代码，换服务只改两行配置。

## 章节目录

1. [01_hello_llm](./01_hello_llm/)：第一次调用——消息三种角色、响应结构、system prompt
2. [02_params_streaming](./02_params_streaming/)：temperature、max_tokens 与流式输出
3. [03_conversation](./03_conversation/)：多轮对话——模型没有记忆，历史要自己维护
4. [04_function_calling](./04_function_calling/)：工具调用循环——让模型操作外部世界
5. [05_errors_retry](./05_errors_retry/)：常见错误、指数退避重试、token 成本估算
6. [06_embeddings_api](./06_embeddings_api/)：Embeddings API——把文本变成向量，为 RAG 打地基
7. [07_structured_outputs](./07_structured_outputs/)：结构化输出进阶——JSON Schema、校验、修复与重试
8. [08_tool_safety](./08_tool_safety/)：工具调用安全——权限、参数校验、审批和审计

## 环境准备

### 1. 安装依赖

`openai` 与 `python-dotenv` 已包含在项目依赖中：

```bash
uv sync
```

### 2. 申请 API 密钥

任选一家服务：OpenAI 官方（需海外网络与付费账号），或国内的 Kimi（Moonshot）、
DeepSeek 等 OpenAI 兼容服务（注册即可创建 API Key，一般按 token 计费）。

### 3. 在项目根目录创建 `.env`

在**仓库根目录**（不是本章节目录）新建 `.env` 文件，写入密钥：

```bash
# .env（已被 .gitignore 忽略，不会提交，也绝不应该提交）
OPENAI_API_KEY=sk-你的密钥
```

如果用的是 OpenAI **兼容服务**（非官方），还要再配两项，以 Kimi（Moonshot）为例：

```bash
OPENAI_BASE_URL=https://api.moonshot.cn/v1
MODEL_NAME=kimi-k2.6
```

> **踩坑预警（真实案例）**：`OPENAI_BASE_URL` 只填到 `/v1` 为止！
> 不要画蛇添足带上接口路径，例如 `https://api.moonshot.cn/v1/chat/completions`。
> SDK 会在 base_url 后面自己拼 `/chat/completions`，你多写一段，最终请求地址就变成
> `.../v1/chat/completions/chat/completions`，得到莫名其妙的 404。
> 症状：密钥明明是对的，却一直报"页面不存在 / Not Found"。

可以直接复制模板再填写（模板里没有真实密钥）：

```bash
cp tutorials/05_llm_api/.env.example .env
```

各章代码统一这样读配置（理解即可，不用背）：

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从当前文件向上查找项目根目录的 .env，读入环境变量
client = OpenAI()  # 自动读取 OPENAI_API_KEY / OPENAI_BASE_URL，无需传参
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
```

### 4. 运行任意一章

统一在**仓库根目录**执行：

```bash
uv run tutorials/05_llm_api/01_hello_llm/main.py
```

## 前置与后续

- 前置：Python 基础语法 + [basic 模块](../02_basic/)的 JSON（请求/响应都是 JSON）。
- 后续：本模块的手写调用是所有上层框架的"裸机版"。学完建议接着看
  [rag 教程](../07_rag/)（给模型外挂知识库，多配一个 Embedding 模型即可）与
  [langchain 教程](../09_langchain/)（把本章的消息、流式、工具调用封装成组件，
  你会发现第 4 章手写的工具循环被框架一行接管）。

## 安全提醒

- `.env` 已在 `.gitignore` 中，**永远不要把密钥提交进 git**，也不要贴到群聊/截图里。
- 密钥泄露后第一时间去服务商控制台**吊销并重置**。

## 常见面试题

**Q1：system、user、assistant 三种角色有什么区别？**

参考答案：system 设置全局行为，user 表示用户输入，assistant 表示模型历史回答。多轮对话需要应用把历史消息再次传给模型。

**Q2：聊天模型和 Embedding 模型有什么区别？**

参考答案：聊天模型输出文本，适合问答和生成；Embedding 模型输出向量，适合语义检索和相似度计算。二者不能混用。

**Q3：temperature 控制什么？**

参考答案：temperature 控制采样随机性。低值更稳定保守，适合 JSON、分类和抽取；高值更多样，适合创意任务。

**Q4：max_tokens 的作用是什么？**

参考答案：它限制模型最多生成多少 token。太小会截断回答，太大可能增加成本和延迟。

**Q5：流式输出的好处是什么？**

参考答案：模型生成一部分就返回一部分，用户更快看到内容，适合聊天和长回答场景。

**Q6：模型是否会自动记住上次对话？**

参考答案：不会。API 默认无跨请求记忆，应用必须把历史消息、摘要或记忆内容放回上下文。

**Q7：工具调用时模型是否真的执行函数？**

参考答案：没有。模型只返回工具名和参数，真正执行由应用代码完成，因此需要校验、权限和审计。

**Q8：为什么要做重试和退避？**

参考答案：模型服务可能限流、超时或临时失败。指数退避能降低瞬时压力，提高稳定性。

**Q9：结构化输出为什么还需要校验？**

参考答案：模型可能输出格式错误、字段缺失或枚举值非法。必须用 JSON Schema 或 Pydantic 校验，并设计修复/重试。

**Q10：OpenAI 兼容服务切换时主要改什么？**

参考答案：通常改 `OPENAI_BASE_URL`、`OPENAI_API_KEY` 和模型名，同时确认服务是否支持所需接口，如 embeddings 和 tool calling。
