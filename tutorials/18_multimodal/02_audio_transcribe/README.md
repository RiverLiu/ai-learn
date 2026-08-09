# 02 语音转写：ASR 与 LLM 的分工

语音转写（ASR，自动语音识别）负责"音频 → 文字"，它和 LLM 是两种模型、两条接口。
moonshot 平台（api.moonshot.cn）目前没有语音转写接口，所以本章不走 `.env` 那套统一配置，
而是采用与 `local_models` 模块相同的**"检测-引导"模式**：检测到本机 whisper 方案就真实转写，
没有就打印本地与云端的接入指引，任何时候运行脚本都有明确收获。

## 本章要点

- **ASR 与 LLM 是管道关系**：ASR 把音频转成文字，LLM 再对文字做摘要、翻译、抽取待办——
  "语音会议纪要"这类产品就是 `ASR → LLM` 两段拼起来的。
- **检测-引导模式**：`importlib.util.find_spec("faster_whisper")` 探测 Python 包，
  `shutil.which("whisper-cli"/"whisper-cpp"/"main")` 探测命令行；都没有则打印指引并正常退出（退出码 0）。
- **本地方案**：faster-whisper（Python 包，纯 CPU 可跑）与 whisper.cpp（C++ 移植，极省内存），
  免费、离线、数据不出本机。
- **云端方案**：OpenAI whisper API（`client.audio.transcriptions.create`）、
  阿里百炼 paraformer-v2 等；换 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 即可切换兼容服务。
- 脚本用标准库 `wave` + `struct` 生成 2 秒 8kHz 正弦波 wav 作演示输入——
  正弦波转不出文字，它的作用是**走通"音频文件 → 转写函数"的调用流程**。

## 运行

```bash
uv run tutorials/18_multimodal/02_audio_transcribe/main.py
```

三种结局，退出码都是 0：

1. 检测到 **faster-whisper**：下载 tiny 模型（首次，约 75 MB）并对演示音频转写；
2. 检测到 **whisper.cpp** 命令行：有 ggml 模型文件（`WHISPER_CPP_MODEL` 指定）则执行转写，
   没有则告诉你下载模型的命令；
3. 都没检测到：打印本地方案（faster-whisper / whisper.cpp）与云端方案
   （OpenAI whisper API / 阿里 paraformer）的接入指引。

本章实测（本机未安装任何 whisper 方案）走的是**第 3 种**：打印完整接入指引并正常退出。
装好 faster-whisper 后重跑即自动进入第 1 种。

## 核心概念

### ASR → LLM：两段管道，各司其职

ASR 模型（如 whisper）只做一件事：把声音波形变成文字。它不理解语义、不会总结。
真正的"智能"在第二段——把转写文字交给 LLM：

```text
会议录音 ──ASR──> 转写文本 ──LLM──> 摘要 / 待办清单 / 翻译 / 问答
```

第二段用的就是前面所有章节讲的 chat completions。所以学多模态的关键不是"一个模型包打天下"，
而是**把不同能力的模型串成管道**：ASR 管耳朵，LLM 管大脑。

### 本地方案对比

| 方案 | 形态 | 特点 |
| --- | --- | --- |
| faster-whisper | Python 包 `pip install faster-whisper` | 推荐入门：几行代码，纯 CPU 可跑，支持 GPU；首次自动下载模型 |
| whisper.cpp | 命令行（macOS: `brew install whisper-cpp`） | C++ 移植，内存占用极小，适合嵌入式/老机器；需另下载 ggml 模型文件 |

两者底层都是 OpenAI 开源的 whisper 模型（tiny / base / small / medium / large 多档，
越大越准越慢，tiny 约 75 MB 足够走通流程）。模型托管在 huggingface.co，首次下载需要能访问。

### 云端方案

不想本地装就用 API，调用形态与聊天接口类似（OpenAI SDK 同一个 client）：

```python
from openai import OpenAI

client = OpenAI()  # 读 OPENAI_API_KEY / OPENAI_BASE_URL
with open("meeting.wav", "rb") as f:
    text = client.audio.transcriptions.create(model="whisper-1", file=f)
print(text.text)
```

换 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 即可切到兼容服务；阿里百炼的 paraformer-v2
是国产语音识别模型，中文场景效果好、自带标点与说话人分离。云端方案按音频时长计费，
适合不想维护模型、音频量不大的场景；注意录音涉及隐私数据时的合规要求。

### 流式语音的场景

本章演示的是"整段音频转文字"（离线批处理）。还有一类**流式 ASR**：边说边出字，
典型场景包括——

- **实时字幕**：直播、视频会议字幕，要求延迟在几百毫秒内；
- **语音助手/车载**：用户说完立刻响应，后面通常紧跟 `ASR → LLM → TTS` 全双工管道；
- **电话客服**：通话中实时转写 + 实时质检。

流式 ASR 一般走 WebSocket 持续上传音频帧（阿里 paraformer、讯飞等都有实时接口），
工程重点是分片、VAD（语音活动检测）与断句，而不是模型本身。

### wav 格式与采样率（附）

wav 是最简单的音频容器：文件头（声道数、位深、采样率）+ 原始 PCM 采样点，
所以用标准库 `wave` + `struct` 就能生成。**采样率**是每秒采样次数（8kHz 是电话音质，
16kHz 是 ASR 常用输入）；**位深**决定每个采样点的精度（16bit 足够语音）。
mp3/m4a 等压缩格式需要解码库（faster-whisper 自带的 PyAV 已覆盖常见格式）。

## 常见错误

1. **`ModuleNotFoundError: faster_whisper`**：包没装，`pip install faster-whisper`
   （或 `uv pip install faster-whisper`）后重跑。本章故意不把它写进项目依赖，避免拖累全仓库。
2. **首次运行卡在模型下载**：whisper 模型托管在 huggingface.co，国内网络可能慢或失败，
   配置镜像（如 `HF_ENDPOINT=https://hf-mirror.com`）后再试。
3. **whisper.cpp 报 `failed to load model`**：只有程序没有 ggml 模型文件，
   按其仓库 `models/download-ggml-model.sh` 下载，并用 `WHISPER_CPP_MODEL` 告诉脚本路径。
4. **真实录音转写效果差**：先查采样率与音质（电话录音 8kHz 单声道效果会打折），
   再把模型从 tiny 升到 small/medium；背景噪音大的先降噪。
5. **把整段长音频直接塞给云端接口**：多数接口有单文件时长/大小限制，长音频先切分
   （按静音处切，避免切断词语），逐段转写再合并。

## 练习建议

1. 安装 faster-whisper 后重跑本章脚本，确认自动进入真实转写分支；再把 `DEMO_WAV`
   换成一段真实中文录音（手机录音转 wav），对比 tiny 与 small 模型的效果与耗时。
2. 把转写结果接进前面的章节：转写一段会议录音后，用 `llm_api` 学到的 chat completions
   生成"三条摘要 + 待办清单"，亲手拼出完整的 `ASR → LLM` 管道。
3. 用 `wave` 模块读一个真实 wav 的声道数/位深/采样率并打印，再把它重采样（或找一段
   不同采样率的音频）观察转写差异，理解"采样率匹配"为什么重要。
4. 调研一个流式 ASR 服务（阿里 paraformer 实时版或讯飞），画出它的 WebSocket
   交互时序图：谁发音频帧、谁发中间结果、最终结果如何确认。
