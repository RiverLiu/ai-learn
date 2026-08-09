# 本地与国产开源模型部署

本仓库的教程统一通过 **OpenAI 兼容接口** 调用模型（`OPENAI_BASE_URL` + `OPENAI_API_KEY` + `MODEL_NAME`）。
这意味着：只要有一个兼容该协议的本地服务，**整套教程不花一分钱 API 费用、不联网也能跑**。
本模块就来做这件事——用 [Ollama](https://ollama.com/) 在自己的电脑上跑开源模型。

## 为什么要在本地跑模型

- **免费**：不限调用次数，做 RAG 这种反复调 Embedding 的实验时尤其划算。
- **隐私**：文档和对话不出本机，适合处理内部资料。
- **离线**：断网、飞机上都能用，也不受 API 限流影响。
- **国产开源模型已经很好用**：通义千问 Qwen3 等国产开源模型在 Ollama 官方模型库直接可拉，
  中文场景下完全够支撑本仓库的全部练习。

代价是需要自己出硬件：模型权重下载占用磁盘，推理占用内存/显存。
第 1 章给出显存与模型大小的选型对照表。

## 章节目录

1. [01_ollama](./01_ollama/)：Ollama 安装与使用，本地跑 Qwen3，OpenAI 兼容端点接入整套教程
2. [02_local_embedding](./02_local_embedding/)：本地向量模型（bge-m3），让 RAG 教程的索引和检索也离线化
3. [03_model_selection](./03_model_selection/)：本地模型选型——聊天、向量、rerank、量化、显存与中文能力

## 环境准备

Python 侧没有新增依赖（`openai`、`httpx`、`numpy` 已在根目录 `pyproject.toml` 中）：

```bash
uv sync
```

两章脚本都采用 **"检测-引导"模式**：启动时先探测本机 Ollama 服务（`http://localhost:11434`）——

- 已安装并运行：直接做真实演示；
- 未安装：打印分步安装与配置指引后正常退出（退出码 0）。

所以没装 Ollama 也可以先运行脚本，照着输出一步步来。

## 配好之后的全局效果

按第 1 章指引在项目根目录 `.env` 写入：

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
MODEL_NAME=qwen3:8b
EMBEDDING_MODEL=bge-m3        # 第 2 章拉取后加上
```

`rag` / `langchain` / `langgraph` / `memory` / `deepagents` 等教程**不需要改任何代码**，
全部改由你本机的开源模型驱动（各章通过 `load_dotenv()` 自动读取根目录 `.env`，
配置模板见根目录 [.env.example](../../.env.example)）。

## 参考

- Ollama 官网与模型库：https://ollama.com/ 、https://ollama.com/library
- Ollama 的 OpenAI 兼容 API 文档：https://docs.ollama.com/openai
- Qwen3 模型卡：https://ollama.com/library/qwen3
- bge-m3 模型卡：https://ollama.com/library/bge-m3
- 模型下载大小、显存需求会随版本变化，**一切以官网模型库的实时数据为准**。

## 常见面试题

**Q1：为什么选择本地模型？**

参考答案：出于隐私、合规、离线、成本和可控性考虑。本地模型适合内部文档和高频实验。

**Q2：本地模型的代价是什么？**

参考答案：需要硬件、模型下载、推理服务维护，并可能在能力、速度和上下文长度上受限。

**Q3：Ollama 的价值是什么？**

参考答案：Ollama 简化本地模型下载、运行和 OpenAI 兼容接口暴露，方便无缝接入教程代码。

**Q4：量化模型有什么优缺点？**

参考答案：量化降低内存/显存占用，但可能损失质量，复杂推理和代码任务尤其要评估。

**Q5：聊天模型和 embedding 模型如何搭配？**

参考答案：聊天模型负责生成，embedding 模型负责检索。常见本地组合是 Qwen 类聊天模型 + bge-m3 embedding。

**Q6：为什么换 embedding 模型要重建索引？**

参考答案：不同模型向量空间不同，旧文档向量不能和新查询向量可靠比较。

**Q7：本地模型如何评估中文能力？**

参考答案：用真实中文问答、RAG、JSON 抽取、中英混合技术问题和长文总结样本测试。

**Q8：参数量越大一定越好吗？**

参考答案：不一定。大模型能力强但更慢更耗资源，实际应按任务、延迟、硬件和评估结果选择。

**Q9：本地模型适合生产吗？**

参考答案：适合部分隐私和成本敏感场景，但需要服务稳定性、监控、并发、权限和模型质量评估。

**Q10：本地模型和云模型如何混合？**

参考答案：可用本地 embedding 和云端强聊天模型，或本地处理敏感任务、云端处理高难任务。
