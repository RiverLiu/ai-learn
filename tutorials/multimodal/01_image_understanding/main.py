"""图像理解：把图片发给视觉模型，让模型"看图说话"。

脚本内容：
1. 用纯标准库（zlib + struct）手写 PNG 编码，生成一张小测试图
   （三条水平彩条 + 一个黄色矩形），不依赖 PIL 等第三方库；
2. 把图片 base64 编码为 data URL，以多模态消息（content 数组：text + image_url）
   发给视觉模型，让模型描述图片、回答"图里有几种颜色、什么形状"；
3. 若当前账号/服务不支持视觉模型（400/403/404 等），打印切换指引并正常退出（退出码 0）。

运行（在仓库根目录）：uv run tutorials/multimodal/01_image_understanding/main.py
"""

import base64
import os
import struct
import sys
import zlib
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

load_dotenv()  # 向上查找项目根目录的 .env，把里面的变量读进环境变量

# 视觉模型名走 VISION_MODEL 环境变量；缺省回落到 kimi-k2.6
# （据 Kimi 开放平台文档，kimi-k2.6 / kimi-k3 原生支持视觉输入，模型名以官网为准：
#  https://platform.kimi.com/docs/models ）
VISION_MODEL = os.getenv("VISION_MODEL", "kimi-k2.6")

REPO_ROOT = Path(__file__).resolve().parents[3]  # 章节目录 → 仓库根目录
TEST_IMAGE_PATH = REPO_ROOT / "tmp" / "multimodal_test_image.png"  # tmp/ 已被 .gitignore 忽略


# ---------------------------------------------------------------------------
# 1. 纯标准库生成 PNG：手写 PNG 文件格式（签名 + IHDR + IDAT + IEND 四个块）
# ---------------------------------------------------------------------------
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    """PNG 块 = 长度(4B) + 类型(4B) + 数据 + CRC32 校验(4B)。"""
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def make_test_png(width: int = 240, height: int = 120) -> bytes:
    """生成测试图：红/绿/蓝三条水平彩条，中间压一个黄色矩形，返回 PNG 字节流。"""
    bands = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # 红、绿、蓝三条彩条
    pixels = [[bands[y * 3 // height]] * width for y in range(height)]
    # 黄色矩形（80≤x<160, 30≤y<90），横跨三条彩条，方便观察模型能否说出叠加关系
    for y in range(30, 90):
        for x in range(80, 160):
            pixels[y][x] = (255, 255, 0)
    # 图像数据：每行扫描线前缀 1 字节过滤器类型（0 = 无过滤），再整体 zlib 压缩
    raw = b"".join(b"\x00" + b"".join(struct.pack("3B", *px) for px in row) for row in pixels)
    # IHDR：宽、高、位深 8、颜色类型 2（真彩色 RGB）、压缩/过滤/隔行均为 0
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"  # PNG 文件签名（固定 8 字节）
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw))
        + _png_chunk(b"IEND", b"")
    )


def to_data_url(png_bytes: bytes) -> str:
    """把图片字节 base64 编码成 data URL——图片不出本机，随请求体一起发给模型。"""
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"


# ---------------------------------------------------------------------------
# 2. 账号/服务不支持视觉模型时的指引（打印后正常退出，退出码 0）
# ---------------------------------------------------------------------------
def print_vision_guide(exc: APIStatusError):
    print(f"调用视觉模型 {VISION_MODEL} 失败（HTTP {exc.status_code}）：")
    print("当前账号/服务大概率不支持该视觉模型。两种解决思路：\n")
    print("【思路 1】核对模型名：登录所用平台的控制台，确认视觉模型 ID 与账号权限")
    print("  （模型名以官网为准，如 Kimi 开放平台 https://platform.kimi.com/docs/models ），")
    print("  然后在项目根目录 .env 中显式指定：VISION_MODEL=<平台提供的视觉模型名>\n")
    print("【思路 2】换用支持视觉的 OpenAI 兼容服务，改 .env 三个变量即可，代码不用动：")
    print("  OPENAI_BASE_URL=<兼容服务地址>   # 只到 /v1 为止")
    print("  OPENAI_API_KEY=<对应服务的密钥>")
    print("  VISION_MODEL=<视觉模型名>        # 如 qwen-vl-plus（阿里百炼）/")
    print("                                  # Qwen/Qwen2.5-VL-7B-Instruct（硅基流动）/ gpt-4o-mini（OpenAI）")
    print("  注意：OPENAI_BASE_URL 一变，MODEL_NAME 也要换成该服务有的聊天模型。")


# ---------------------------------------------------------------------------
# 3. 发送多模态消息：content 从字符串变成数组（text + image_url）
# ---------------------------------------------------------------------------
def describe_image():
    png_bytes = make_test_png()
    TEST_IMAGE_PATH.parent.mkdir(exist_ok=True)
    TEST_IMAGE_PATH.write_bytes(png_bytes)  # 留一份在磁盘上，方便打开对照模型的描述
    print(f"已生成测试图：{TEST_IMAGE_PATH}")
    print("  （240x120，红/绿/蓝三条水平彩条 + 中间一个黄色矩形）")
    print(f"使用视觉模型：{VISION_MODEL}（可用 VISION_MODEL 环境变量覆盖）\n")

    # OpenAI() 自动读取环境变量 OPENAI_API_KEY 和 OPENAI_BASE_URL，与前面各章一致
    client = OpenAI()
    question = "请描述这张图片：图里有几种颜色？分别是什么形状、在什么位置？"
    try:
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [  # 多模态消息：content 是数组，文本和图片各占一项
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": to_data_url(png_bytes)}},
                    ],
                }
            ],
        )
    except APIStatusError as exc:
        if exc.status_code in (400, 403, 404):  # 模型不存在 / 无权限 / 不支持图片输入
            print_vision_guide(exc)
            return
        print(f"API 返回错误（HTTP {exc.status_code}）：{exc.message}")
        sys.exit(1)
    except APIConnectionError as exc:
        print(f"网络连接失败：{exc}\n排查：确认 OPENAI_BASE_URL 可达、网络正常。")
        sys.exit(1)

    print(f"【提问】{question}")
    print(f"【模型回答】{resp.choices[0].message.content}")
    if resp.usage:
        # 图片会被折算成 token 计入输入用量，通常比一段文字贵一个量级
        print(
            f"\ntoken 用量：输入 {resp.usage.prompt_tokens}（含图片折算）"
            f" + 输出 {resp.usage.completion_tokens} = 共 {resp.usage.total_tokens} token"
        )


def main():
    describe_image()


if __name__ == "__main__":
    main()
