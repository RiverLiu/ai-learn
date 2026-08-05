# LLM 应用安全：提示词注入与纵深防御

LLM 应用把"不可信输入"和"高权限能力"（读知识库、调工具、发邮件）接在了一起，
这是传统 Web 安全里从未有过的组合。本模块用真实 API 调用演示两类最典型的攻击，
以及一套不依赖"模型自觉"的工程防线。

## 威胁全景

- **直接提示词注入**：攻击者亲自对模型说话，套取系统提示词、内部数据，
  或让模型做分外之事。
- **间接提示词注入**：攻击者把恶意指令藏进模型会读到的资料里
  （网页、邮件、知识库文档），模型读到后照做——用户根本没意识到攻击发生。
- **纵深防御（Defense in Depth）**：假设提示词防线终将被突破，
  在数据、工具、密钥三个层面布置不依赖模型的工程措施，让攻击
  "成了也拿不到什么"。

```
攻击者 ──直接注入──▶ LLM 应用
攻击者 ──投毒资料──▶ 知识库/网页 ──间接注入──▶ LLM 应用
                                                │
防线：提示词加固（可赌输）→ 输出检查 → 数据脱敏 → 工具权限门 → 密钥卫生
```

## 章节目录

1. [01_prompt_injection](./01_prompt_injection/)：直接注入——六类手法套取
   客服 bot 的内部暗号，加固提示词重放对比
2. [02_indirect_injection](./02_indirect_injection/)：间接注入——RAG 知识库里的
   投毒文档，以及"定界符 + 指令声明 + 输出拦截"三道防线
3. [03_defense_in_depth](./03_defense_in_depth/)：纵深防御清单——数据脱敏、
   工具最小权限（白名单 + 审批门）、密钥卫生

## 环境准备

依赖已包含在项目根目录 `pyproject.toml`（`openai`、`python-dotenv`），执行 `uv sync`。
三章都需要调用聊天模型，先配置密钥（见根目录 `.env.example`）：

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://..."   # 兼容服务时
export MODEL_NAME="..."                # 默认 gpt-4o-mini
```

## 一个必须记住的事实

提示词注入目前没有"银弹"。提示词加固、输入过滤、输出检查都只是抬高攻击成本，
**攻击成功与否取决于模型能力和具体措辞**。所以本模块的立场是：
演示攻击 → 演示提示词级防御 → 承认它可被绕过 → 落地工程级纵深防御。

## 参考

- OWASP Top 10 for LLM Applications：https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Simon Willison 的提示词注入系列文章：https://simonwillison.net/series/prompt-injection/
