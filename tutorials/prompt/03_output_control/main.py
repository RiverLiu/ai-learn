"""强制 JSON 输出：从"说一句用 JSON"到"程序能解析的 JSON"。

- 坏提示词：只说"用 JSON 返回" → 模型输出带 ```json 围栏（甚至夹带废话），
  json.loads 直接报错；
- 好提示词：写明 schema（字段名 + 类型）+ "只输出 JSON，不要围栏、不要解释"
  → 解析一次成功；
- 工程兜底：即便如此，线上也要假设模型有失手的时候——
  try/except 接住解析错误，把错误信息反馈给模型"重问一次"。
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置约定：密钥与接口地址走环境变量（或 .env 文件），不写进代码
load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
client = OpenAI()  # 自动读取 OPENAI_API_KEY 与 OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

REVIEW = "云雀笔记用了两个月，同步速度比以前快多了，就是导出 PDF 经常失败，挺闹心的。总体还行，给 3 星吧。"

# ---------- 坏提示词：只说"用 JSON 返回"，不说字段、不说不要围栏 ----------
BAD_SYSTEM = "你是一个乐于助人的助手。"
BAD_USER = (
    f"这是一条用户评论：\n{REVIEW}\n"
    "请把评论信息用 JSON 返回给我，字段包括 product、rating（数字）、pros（列表）、cons（列表）。"
)

# ---------- 好提示词：明确 schema + 明确"只输出 JSON" ----------
GOOD_SYSTEM = """你是一个信息抽取程序。从用户评论中抽取信息，输出为一个 JSON 对象，字段如下：
- product: 字符串，产品名
- rating: 数字，星级（1-5 的整数）
- pros: 字符串列表，评论中提到的优点
- cons: 字符串列表，评论中提到的缺点
要求：只输出 JSON 本身，不要用 markdown 代码围栏包裹，不要输出任何解释。"""


def chat(messages: list[dict]) -> str:
    """一次 LLM 调用；传入完整消息列表，方便演示多轮'重问'。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2500,  # 思考型模型会先消耗推理 token，预算要给足
    )
    return response.choices[0].message.content or ""


def extract_with_retry(system: str, user: str) -> dict | None:
    """工程兜底：调模型 → 解析 → 失败就把错误反馈给模型重问一次。

    返回解析出的字典；重问一次仍失败则返回 None（调用方走人工/默认值流程）。
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    for attempt in range(2):  # 首次 + 重问一次，共两次机会
        raw = chat(messages)
        try:
            return json.loads(raw)  # 成功：直接返回结构化结果
        except json.JSONDecodeError as e:
            print(f"  [第 {attempt + 1} 次] json.loads 失败：{e}")
            if attempt == 1:
                break
            # 把模型的原话和报错一起喂回去，让它修正——多轮对话的一个典型用法
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": "上面的回答无法被 json.loads 解析。请重新输出："
                           "只输出 JSON 本身，不要 markdown 围栏，不要任何解释。",
            })
    return None


def main():
    # ===== 1. 坏提示词：模型很"热心"，输出却解析不了 =====
    print("===== 1. 坏提示词：只说'用 JSON 返回' =====")
    bad_raw = chat([
        {"role": "system", "content": BAD_SYSTEM},
        {"role": "user", "content": BAD_USER},
    ])
    print(f"模型输出：\n{bad_raw}")
    try:
        json.loads(bad_raw)
        print("解析结果：成功（运气好）")
    except json.JSONDecodeError as e:
        print(f"解析结果：失败 —— {type(e).__name__}: {e}")
        print("原因：```json 围栏不是合法 JSON 的一部分，json.loads 只认纯 JSON 文本。")

    # ===== 2. 好提示词：schema + 只输出 JSON，一次成功 =====
    print("\n===== 2. 好提示词：明确 schema + 只输出 JSON =====")
    good_raw = chat([
        {"role": "system", "content": GOOD_SYSTEM},
        {"role": "user", "content": REVIEW},
    ])
    print(f"模型输出：\n{good_raw}")
    data = json.loads(good_raw)  # 好提示词下这一步应直接成功
    print(f"解析结果：成功 —— rating={data['rating']}，cons={data['cons']}")

    # ===== 3. 工程兜底：故意用坏提示词，演示"失败 → 重问 → 救回来" =====
    print("\n===== 3. 兜底处理：解析失败时重问一次 =====")
    print("（故意仍用坏提示词触发失败，演示 extract_with_retry 的自救过程）")
    result = extract_with_retry(BAD_SYSTEM, BAD_USER)
    if result is None:
        print("两次都失败：返回 None，线上应走人工处理或默认值流程。")
    else:
        print(f"重问后解析成功：{result}")

    print("\n===== 小结 =====")
    print("- '用 JSON 返回'只是愿望；'schema + 只输出 JSON + 不要解释'才是可解析的契约。")
    print("- 提示词再严，也要留 try/except 兜底：模型输出永远是概率，不是保证。")


if __name__ == "__main__":
    main()
