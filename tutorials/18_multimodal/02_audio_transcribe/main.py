"""语音转写（ASR）：检测本机 whisper 方案并转写，否则打印方案指引。

moonshot 平台（api.moonshot.cn）目前没有语音转写接口，本章采用"检测-引导"模式，
保证任何时候都能运行：
1. 先用标准库生成一段 2 秒 8kHz 正弦波 wav 作演示输入——正弦波不含语音，
   转不出文字，它的作用是走通"音频文件 → 转写函数"的完整调用流程；
2. 检测到 faster-whisper（Python 包）：直接对演示音频做转写；
   检测到 whisper.cpp（命令行）：在有 ggml 模型文件时执行转写；
3. 都没检测到：打印本地方案（faster-whisper / whisper.cpp）与云端方案
   （OpenAI whisper API、阿里 paraformer）的接入指引，正常退出（退出码 0）。

运行（在仓库根目录）：uv run tutorials/18_multimodal/02_audio_transcribe/main.py
"""

import importlib.util
import math
import os
import shutil
import struct
import subprocess
import wave
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # 章节目录 → 仓库根目录
DEMO_WAV = REPO_ROOT / "tmp" / "multimodal_demo_tone.wav"  # tmp/ 已被 .gitignore 忽略

# 演示音频参数：2 秒、8kHz 采样、16bit 单声道、440Hz（钢琴中央 A）正弦波
SAMPLE_RATE = 8000
SECONDS = 2
FREQ = 440.0


# ---------------------------------------------------------------------------
# 1. 纯标准库生成 wav：wave 模块写文件头，struct 打包 PCM 采样点
# ---------------------------------------------------------------------------
def make_demo_wav(path: Path):
    """生成 2 秒 440Hz 正弦波 wav。它只是"一段有声音的音频"，供走通转写流程用。"""
    frames = b"".join(
        struct.pack("<h", int(32767 * 0.5 * math.sin(2 * math.pi * FREQ * i / SAMPLE_RATE)))
        for i in range(SAMPLE_RATE * SECONDS)
    )
    path.parent.mkdir(exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)  # 单声道
        f.setsampwidth(2)  # 16bit = 2 字节
        f.setframerate(SAMPLE_RATE)
        f.writeframes(frames)


# ---------------------------------------------------------------------------
# 2. 检测：faster-whisper 用 import 探测；whisper.cpp 用 which 探测命令行
# ---------------------------------------------------------------------------
def detect_faster_whisper() -> bool:
    """faster-whisper 是 Python 包：能找到模块 spec 即视为已安装。"""
    return importlib.util.find_spec("faster_whisper") is not None


def detect_whisper_cpp() -> str | None:
    """whisper.cpp 是命令行程序：新版叫 whisper-cli，旧版叫 main，brew 版叫 whisper-cpp。"""
    for name in ("whisper-cli", "whisper-cpp", "main"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None


# ---------------------------------------------------------------------------
# 3a. 用 faster-whisper 转写
# ---------------------------------------------------------------------------
def transcribe_with_faster_whisper():
    from faster_whisper import WhisperModel

    print("检测到 faster-whisper，开始转写（首次运行自动下载 tiny 模型，约 75 MB）…")
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(DEMO_WAV))
        texts = [seg.text.strip() for seg in segments]
    except Exception as exc:  # 模型下载失败、磁盘不足等
        print(f"转写失败：{exc}")
        print("排查：确认网络可达 huggingface.co（模型托管站）；或换更小的模型/检查磁盘空间。")
        raise SystemExit(1)
    print(f"识别语言：{info.language}（置信度 {info.language_probability:.2f}）")
    if texts:
        print(f"转写结果：{' '.join(texts)}")
    else:
        print("转写结果为空——正弦波不含语音内容，属预期现象，流程已走通。")
        print("把 DEMO_WAV 换成真实录音（如会议、播客 wav/mp3）即可得到文字。")


# ---------------------------------------------------------------------------
# 3b. 用 whisper.cpp 转写（需要另行准备 ggml 模型文件）
# ---------------------------------------------------------------------------
def transcribe_with_whisper_cpp(exe: str):
    model_path = os.getenv("WHISPER_CPP_MODEL", "")
    if not model_path or not Path(model_path).exists():
        print(f"检测到 whisper.cpp（{exe}），但还没有 ggml 模型文件。")
        print("请先到 whisper.cpp 仓库下载模型（tiny 约 75 MB）：")
        print("  bash ./models/download-ggml-model.sh tiny")
        print("然后指定模型路径重跑本脚本：")
        print(f"  WHISPER_CPP_MODEL=/path/to/ggml-tiny.bin uv run tutorials/18_multimodal/02_audio_transcribe/main.py")
        return
    cmd = [exe, "-m", model_path, "-f", str(DEMO_WAV)]
    print(f"使用 whisper.cpp 转写：{' '.join(cmd)}\n")
    subprocess.run(cmd, check=False)
    print("\n（正弦波一般转不出文字，属预期现象；把 -f 换成真实录音即可。）")


# ---------------------------------------------------------------------------
# 3c. 本机没有任何 whisper 方案时：打印本地 + 云端接入指引，正常退出
# ---------------------------------------------------------------------------
def print_guide():
    print("未检测到本机 whisper 方案（faster-whisper / whisper.cpp）。任选一种接入：\n")
    print("【本地方案 1】faster-whisper（Python 包，推荐；装完重跑本脚本即自动转写）")
    print("  pip install faster-whisper        # 或 uv pip install faster-whisper")
    print("  首次运行自动下载 tiny 模型（约 75 MB），纯 CPU 可跑，支持 GPU 加速\n")
    print("【本地方案 2】whisper.cpp（C++ 移植，极省内存）")
    print("  macOS：brew install whisper-cpp；其他平台见 github.com/ggml-org/whisper.cpp")
    print("  另需下载 ggml 模型文件，命令行用法：whisper-cli -m ggml-tiny.bin -f 音频.wav\n")
    print("【云端方案】不想本地安装：调用 OpenAI 兼容的语音接口")
    print("  OpenAI：client.audio.transcriptions.create(model='whisper-1', file=open('a.wav', 'rb'))")
    print("  换 OPENAI_BASE_URL + OPENAI_API_KEY 即可切到兼容服务；")
    print("  阿里百炼 paraformer-v2（语音识别模型）提供同类能力，中文效果好。")
    print("  注意：moonshot（api.moonshot.cn）目前不提供语音转写接口，故本章不走 .env 那套配置。\n")
    print(f"装好任意一种后重跑：uv run tutorials/18_multimodal/02_audio_transcribe/main.py")


def main():
    make_demo_wav(DEMO_WAV)
    print(f"已生成演示音频：{DEMO_WAV}")
    print("  （2 秒 440Hz 正弦波，8kHz 16bit 单声道；正弦波转不出文字，只为走通流程）\n")

    if detect_faster_whisper():
        transcribe_with_faster_whisper()
    elif exe := detect_whisper_cpp():
        transcribe_with_whisper_cpp(exe)
    else:
        print_guide()
    # 三条分支都正常结束，退出码 0


if __name__ == "__main__":
    main()
