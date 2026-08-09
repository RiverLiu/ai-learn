# 01 Ollama：在本地跑开源大模型

Ollama 是目前最省心的本地模型运行工具：一条命令下载模型权重，一条命令开始对话，
还自带 **OpenAI 兼容的 HTTP 端点**——这正是让本仓库整套教程脱离 OpenAI 也能跑的关键。
本章以国产开源模型 **Qwen3** 为例，完成"安装 → 拉模型 → 对话 → 代码调用"全流程。

## 本章要点

- `ollama pull qwen3:8b` 下载模型，`ollama run qwen3:8b` 命令行直接对话，权重缓存在本机，之后秒级启动。
- Ollama 服务监听 `http://localhost:11434`，其 **`/v1` 路径兼容 OpenAI 协议**，
  所以 `openai` SDK 只需改 `base_url` 和 `api_key`（填任意非空串，约定俗成 `ollama`）即可调用本地模型。
- 在项目根目录 `.env` 配好 `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `MODEL_NAME` 三个变量后，
  `rag`、`langchain`、`langgraph`、`deepagents` 等教程**原样可用**，不需要改一行代码。
- 模型越大效果越好但越吃内存/显存；选型见下文对照表，下载大小与硬件要求以官网模型库实时数据为准。

## 运行

```bash
uv run tutorials/16_local_models/01_ollama/main.py
```

脚本是"检测-引导"模式：

- 检测到本机 Ollama 在线：通过 OpenAI 兼容端点做一次普通对话 + 一次流式输出；
- 未检测到：打印下面的分步安装指引并正常退出（退出码 0）。

## 核心概念

### 安装 Ollama

- **macOS**：到 https://ollama.com/download/mac 下载 `Ollama.dmg`，把 Ollama.app 拖进"应用程序"并启动；
  或用 Homebrew：`brew install --cask ollama`。
- **Linux**：`curl -fsSL https://ollama.com/install.sh | sh`
- **Windows**：到 https://ollama.com/download/windows 下载 `OllamaSetup.exe` 安装（需 Windows 10 及以上）。

装完验证（桌面版启动后命令行即可用；Linux 上服务由 `ollama serve` 提供，安装脚本已配置为系统服务）：

```bash
ollama --version
```

### 拉取并运行模型

```bash
ollama pull qwen3:8b     # 下载模型权重（约 5 GB，只需一次）
ollama run qwen3:8b      # 进入交互式对话，输入 /bye 退出
ollama list              # 查看本机已安装的模型
ollama rm qwen3:8b       # 删除模型，释放磁盘
```

`ollama run` 时如果模型没拉过会自动先下载。首次运行把权重读入内存/显存较慢，之后常驻、响应很快。

### OpenAI 兼容端点：一套代码，本地云端随便换

Ollama 启动后监听 `11434` 端口，其中 `http://localhost:11434/v1` 实现了 OpenAI 的
`/chat/completions`、`/embeddings` 等接口。调用时只需把 SDK 指过来：

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

`api_key` 不会被校验，但 SDK 要求非空，约定俗成填 `"ollama"`。

对本仓库更省事的做法是写进项目根目录的 `.env`（模板见根目录 `.env.example`，各章代码自动读取）：

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
MODEL_NAME=qwen3:8b
```

配好后 `rag` / `langchain` / `langgraph` / `memory` / `deepagents` 教程**全部原样可用**——
因为它们本来就是按"OpenAI 兼容服务"写的，只认这三个环境变量，不认厂商。

### 模型选型：显存/内存与模型大小对照

Ollama 默认拉取 Q4 量化版本，资源占用远小于原始权重。以 Qwen3 系列为例
（下载大小、上下文长度等以 https://ollama.com/library/qwen3 的实时数据为准）：

| 模型 | 建议内存/显存 | 适用场景 |
| --- | --- | --- |
| `qwen3:0.6b` / `qwen3:1.7b` | 4 GB | 老机器、快速验证流程 |
| `qwen3:4b` | 4–6 GB | 入门级独显、轻薄本 |
| `qwen3:8b`（本章默认） | 8 GB 左右 | 大多数 16 GB 内存的 Mac / PC，效果与速度平衡 |
| `qwen3:14b` | 12 GB 左右 | 12 GB 独显、32 GB 内存的 Mac |
| `qwen3:32b` | 20–24 GB | 高端显卡（如 24 GB 显存）、大内存工作站 |

经验法则：**可用内存/显存 ≥ 模型下载大小 × 1.2** 就能流畅跑；不够就降一档，量化模型在 CPU 上也能跑，只是慢。
Apple Silicon Mac 的统一内存即显存，16 GB 机型跑 8B 很从容。

## 常见错误

1. **`Connection refused` / 脚本提示服务不在线**：Ollama 没在运行。macOS/Windows 启动 Ollama 应用即可；
   Linux 执行 `ollama serve`（或 `systemctl start ollama`）。
2. **`model 'qwen3:8b' not found`**：服务在线但模型没拉，先 `ollama pull qwen3:8b`。可用 `ollama list` 核对名字和 tag。
3. **模型名拼错 tag**：Ollama 模型名是 `名字:标签` 格式（如 `qwen3:8b`），标签必须照
   [官网模型库](https://ollama.com/library) 抄，`qwen3:8B`、`qwen-3:8b` 都会找不到。
4. **回答极慢、风扇狂转**：模型相对硬件太大了，换小一档（如 `qwen3:4b`），改 `.env` 里 `MODEL_NAME` 即可，代码不用动。
5. **`OPENAI_BASE_URL` 多写了路径**：只到 `/v1` 为止，不要带 `/chat/completions` 后缀（与根目录 `.env.example` 的注释一致）。

## 练习建议

1. 拉一个小模型 `ollama pull qwen3:4b`，与本章默认的 8B 对比同一问题的回答质量和速度。
2. 不配 SDK，直接用 `curl http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d '{...}'`
   发一次请求，体会"兼容协议"意味着任何会调 OpenAI 的工具都能调本地模型。
3. 按上文配好项目根目录 `.env`，然后运行 `uv run tutorials/07_rag/04_rag_pipeline/main.py`
   （需先完成下一章的本地 Embedding 配置），观察整条 RAG 流水线全部由本地模型驱动。
