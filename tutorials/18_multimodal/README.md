# 多模态：图像理解与语音转写

LLM 应用不只有文字：用户会发截图、照片，也会发语音、传会议录音。
本模块面向**在职工程师**，用两章讲清多模态落地的两种核心形态——
**图像理解**（图片 → 视觉模型 → 文字）与**语音转写**（音频 → ASR → 文字），
以及它们与前面章节学过的 chat completions 如何拼成完整管道。

## 章节目录

1. [01_image_understanding](./01_image_understanding/)：多模态消息结构（content 数组）、
   base64 data URL 与公网 URL 两种给图方式、图片 token 计费
2. [02_audio_transcribe](./02_audio_transcribe/)：ASR 与 LLM 的管道关系（转写 → 摘要）、
   本地 whisper 方案与云端语音接口、流式语音场景
3. [03_multimodal_workflows](./03_multimodal_workflows/)：图片、OCR、语音、文本如何组合成真实业务流程

## 环境准备

没有新增 Python 依赖（`openai`、`python-dotenv` 已在根目录 `pyproject.toml` 中）：

```bash
uv sync
```

第 1 章沿用全仓库统一配置（项目根目录 `.env` 的 `OPENAI_API_KEY` / `OPENAI_BASE_URL` /
`MODEL_NAME`），另加一个可选变量指定视觉模型：

```bash
VISION_MODEL=kimi-k2.6   # 缺省即此值；视觉模型 ID 以各平台官网实时列表为准
```

第 2 章采用**"检测-引导"模式**（与 `local_models` 模块一致）：moonshot 平台没有语音接口，
脚本改为检测本机的 faster-whisper / whisper.cpp——有就真实转写，没有就打印本地与云端
接入指引后正常退出（退出码 0），所以什么都没装也可以先跑起来照着做。

## 学完能做什么

- 给用户消息里塞图片（工单截图、报错照片），让模型直接看图回答；
- 搭一条 `录音 → ASR 转写 → LLM 摘要/待办` 的会议纪要管道；
- 判断一个多模态需求该用云端接口还是本地模型（成本、隐私、延迟三个维度）。
- 设计 `图片/音频 → 结构化文本 → LLM → 业务结果` 的多模态应用流程。
