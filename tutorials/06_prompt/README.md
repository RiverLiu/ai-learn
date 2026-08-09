# Prompt Engineering 教程：提示词工程

调模型时，模型是同一个模型，**提示词不同，输出质量天差地别**。
如果说"会调 API"是 AI 开发的第一课，那提示词工程就是第一课之外最重要的软技能：

- **零成本见效**：不用训练模型、不用改代码架构，改写几行文字就能提升效果；
- **跨模型通用**：四要素、few-shot、输出控制、思维链这些方法，换任何模型都适用；
- **一切上层应用的地基**：RAG、Agent、工具调用，拆开看每一层都是在跟模型"把话说清楚"。

本模块共 5 章，每章都用真实 API 做"坏提示词 vs 好提示词"的并排对比，
让差距自己说话。场景统一围绕一个虚构的笔记软件"云雀笔记"——正因为它不存在，
模型对它一无所知，提示词的好坏才会暴露得最彻底。

## 章节目录

1. [01_anatomy](./01_anatomy/)：提示词四要素——角色、任务、约束、输出格式
2. [02_fewshot](./02_fewshot/)：zero-shot vs few-shot——用示例传递"分类标准"
3. [03_output_control](./03_output_control/)：强制 JSON 输出与解析失败的兜底
4. [04_reasoning](./04_reasoning/)：思维链——先推理后答案，再自我检查
5. [05_iteration](./05_iteration/)：提示词迭代方法论——用数据而不是感觉调提示词
6. [06_prompt_boundaries](./06_prompt_boundaries/)：提示词边界——安全、权限和系统规则不能只靠 prompt

## 环境准备

依赖已包含在项目根目录的 `pyproject.toml` 中（`openai`、`python-dotenv`）：

```bash
uv sync
```

代码走 OpenAI 兼容协议，通过环境变量（或仓库根目录的 `.env` 文件）配置，
**不要把密钥写进代码**：

```bash
export OPENAI_API_KEY="sk-..."
# 使用兼容服务时追加（以 Moonshot 为例）：
export OPENAI_BASE_URL="https://api.moonshot.cn/v1"
export MODEL_NAME="kimi-k2.6"
```

运行任意一章（每章都会真实调用 API，产生少量费用）：

```bash
uv run tutorials/06_prompt/01_anatomy/main.py
```

## 前置与后续

- 前置：只需 Python 基础语法；没调过 LLM API 也没关系，第 1 章的调用代码只有几行。
- 后续：提示词写好后，可用 [langchain 教程](../09_langchain/)的提示词模板与输出解析器
  把提示词工程化；第 5 章的"评估集打分"思路，会在 evaluation（评估）模块中扩展成完整体系。

## 一个诚实的提醒

模型越强，"坏提示词"与"好提示词"的差距越小——强模型会自己补全你没说清的意图。
本模块的演示在强模型上差异可能不如弱模型戏剧化，但**方法是通用的**：
约束越少，模型自由发挥的空间越大，输出就越不可控。线上系统赌不起"模型这次心情好"。
