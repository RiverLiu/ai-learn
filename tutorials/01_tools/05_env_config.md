# 05 环境变量与配置管理

AI 应用通常依赖模型服务、向量模型、数据库、缓存、对象存储等外部系统。密钥和服务地址不能写死在代码里，
应该通过环境变量或 `.env` 文件管理。

## 本章要点

- `.env` 适合本地开发配置，真实密钥不要提交到 git。
- 环境变量是应用读取配置的统一入口。
- `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL_NAME`、`EMBEDDING_MODEL` 是本教程的核心配置。
- 聊天模型和向量模型可能来自不同服务，生产项目要分开配置。

## `.env` 是什么

`.env` 是一个普通文本文件：

```text
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.example.com/v1
MODEL_NAME=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

Python 程序可以用 `python-dotenv` 读取它：

```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL_NAME", "gpt-4.1-mini")
```

## 本教程的统一配置

根目录 `.env.example` 是模板，可以复制为 `.env`：

```bash
cp .env.example .env
```

常用字段：

| 变量 | 作用 | 示例 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 模型服务密钥 | `sk-...` |
| `OPENAI_BASE_URL` | OpenAI 兼容服务地址 | `https://api.openai.com/v1` |
| `MODEL_NAME` | 聊天模型 | `gpt-4.1-mini` |
| `EMBEDDING_MODEL` | 向量模型 | `text-embedding-3-small` |

注意：`OPENAI_BASE_URL` 只写到 `/v1`，不要写 `/chat/completions` 或 `/embeddings`。
SDK 会自动拼接具体接口路径。

## 聊天模型和向量模型分开配置

很多服务只提供聊天模型，不提供 embedding。比如你可能这样组合：

```text
聊天模型：Kimi / DeepSeek / OpenAI
向量模型：OpenAI / 百炼 / 智谱 / 本地 Ollama
```

如果两类模型不在同一个兼容端点下，单一 `OPENAI_BASE_URL` 就不够了。生产项目通常会拆成：

```text
CHAT_API_KEY=...
CHAT_BASE_URL=...
CHAT_MODEL=...

EMBEDDING_API_KEY=...
EMBEDDING_BASE_URL=...
EMBEDDING_MODEL=...
```

本教程为了保持入门简单，大部分章节使用统一的 `OPENAI_*` 配置。

## 配置分层

常见环境：

| 环境 | 配置来源 | 特点 |
| --- | --- | --- |
| 本地开发 | `.env` | 方便调试，不提交 |
| 测试环境 | CI secrets | 自动化测试使用 |
| 生产环境 | 部署平台 Secret | 权限严格、可轮换 |

不要把生产密钥写入：

- 代码文件
- README 截图
- 测试数据
- Docker 镜像
- 前端代码

## 常见错误

**错误：把 `.env` 提交到 git。**

后果：密钥泄露。解法：`.env` 必须在 `.gitignore` 中，只提交 `.env.example`。

**错误：本地改了 `.env` 但程序不生效。**

可能原因：当前 shell 已经 `export` 了同名变量，优先级高于 `.env`。可以先执行：

```bash
unset OPENAI_API_KEY
unset OPENAI_BASE_URL
```

**错误：把模型名写死在代码里。**

后果：切换模型时要改很多文件。推荐统一从 `MODEL_NAME` 读取。

## 练习

1. 复制 `.env.example` 为 `.env`。
2. 设置 `MODEL_NAME` 为你当前使用的聊天模型。
3. 运行 `tutorials/05_llm_api/01_hello_llm/main.py`。
4. 修改 `MODEL_NAME` 后再次运行，观察输出是否仍正常。
