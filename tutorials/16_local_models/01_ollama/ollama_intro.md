# Ollama 介绍

## 什么是 Ollama

[Ollama](https://ollama.com/) 是一个开源的本地大模型运行工具，目标是让"在自己电脑上跑大语言模型"
变成一件一条命令就能完成的事：

```bash
ollama run qwen3:8b
```

它把模型权重的下载、量化、加载、推理、服务化全部打包进一个工具里，
免去了手动下载权重、配置推理框架、写服务代码这一整套繁琐流程。

## 核心特性

- **开箱即用**：Windows / macOS / Linux 全平台支持，装完即用，无需 CUDA 等复杂配置。
- **模型库即拉即跑**：官方模型库（https://ollama.com/library）收录了 Qwen、Llama、DeepSeek、
  Gemma 等主流开源模型，`ollama pull <模型名>` 一条命令下载，自动选合适的量化版本。
- **跨硬件推理**：底层基于 GGUF 格式与 llama.cpp 推理引擎，有 GPU 走 GPU，
  纯 CPU 也能跑（只是慢），Apple Silicon 的统一内存直接被当作显存使用。
- **自带 HTTP 服务**：启动后监听 `http://localhost:11434`，其中 `/v1` 路径
  **兼容 OpenAI 协议**，任何会调 OpenAI 的 SDK / 框架（LangChain、LlamaIndex 等）
  只需改 `base_url` 即可切换到本地模型。
- **Modelfile 自定义**：类似 Dockerfile，可以通过 `Modelfile` 基于已有模型定制
  系统提示词、参数、模板，构建自己的模型变体。

## 工作原理简览

```
ollama run qwen3:8b
        │
        ▼
┌─────────────┐   未下载则先从模型库拉取（GGUF 量化权重，缓存在本机）
│  模型权重缓存  │
└─────────────┘
        │
        ▼
┌─────────────┐   llama.cpp 推理引擎加载权重到内存/显存并常驻
│  Ollama 服务  │   监听 localhost:11434
└─────────────┘
        │
        ├── CLI 交互式对话（ollama run）
        ├── 原生 API（/api/generate、/api/chat）
        └── OpenAI 兼容 API（/v1/chat/completions、/v1/embeddings）
```

关键点：**模型常驻内存/显存**。首次加载较慢，之后的请求都是秒级响应；
一段时间无请求后模型会被自动卸载以释放资源。

## 常用命令速览

```bash
ollama pull qwen3:8b    # 下载模型
ollama run qwen3:8b     # 运行并进入对话（未下载会自动先拉取）
ollama list             # 列出本机已有模型
ollama ps               # 查看当前加载在内存中的模型
ollama rm qwen3:8b      # 删除模型
ollama serve            # 手动启动服务（桌面版通常已后台运行）
```

## 适合用在哪

- **学习实验**：免费、不限次数，适合反复调试提示词、RAG、Agent 等流程（本仓库教程的典型用法）。
- **隐私敏感场景**：数据不出本机，可处理内部文档。
- **离线环境**：断网可用。
- **原型验证**：先本地跑通，再一键切换到云端 API（得益于 OpenAI 兼容协议，代码零改动）。

不适合：追求最强模型能力（本地能跑的模型规模有限）、高并发生产服务
（此时应选 vLLM、TGI 等专门的服务框架）。

## 下一步

安装与使用的完整分步指引见本章 [README.md](./README.md)。
