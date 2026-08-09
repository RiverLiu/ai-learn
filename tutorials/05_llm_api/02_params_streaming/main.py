"""最常用的请求参数与流式输出：temperature、max_tokens、stream。

- temperature：回答的"随机程度"，0 最确定，越大越野（范围一般 0~2）。
- max_tokens：回答的最大长度，超了会被硬截断（finish_reason="length"）。
- stream=True：不等全部生成完，逐块返回——聊天界面"打字机效果"的来源。

运行（在仓库根目录）：uv run tutorials/05_llm_api/02_params_streaming/main.py
"""

import os
import time

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 向上查找项目根目录 .env
client = OpenAI()  # 自动读取 OPENAI_API_KEY / OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def ask(question: str, temperature: float | None = None):
    """封装一次调用。

    注意：部分模型（如一些思考型模型）由服务商锁定 temperature，不允许调用方设置，
    强行传参会报 400。这时退化为不传该参数、用模型默认值——同一份代码两边都能跑。
    """
    kwargs = dict(model=MODEL, messages=[{"role": "user", "content": question}])
    if temperature is not None:
        kwargs["temperature"] = temperature
    try:
        return client.chat.completions.create(**kwargs)
    except openai.BadRequestError as e:
        if temperature is not None and "temperature" in str(e):
            print(f"  （当前模型不允许设置 temperature={temperature}，改用模型默认值）")
            del kwargs["temperature"]
            return client.chat.completions.create(**kwargs)
        raise


# ---------------------------------------------------------------------------
# 1. temperature：同一道创意题，0 vs 2 各跑一次
# ---------------------------------------------------------------------------
def temperature_demo():
    """创意题最能体现差异：temperature=0 保守稳定，temperature=2 天马行空。"""
    question = "给一家开在大学旁边的猫咖起一个店名，并配一句广告语。"
    for temp in [0.0, 2.0]:
        response = ask(question, temperature=temp)  # 0 = 几乎每次一样；越大越发散
        print(f"【temperature={temp}】")
        print(f"  {response.choices[0].message.content}\n")
    print("  → 对比两次输出是否不同；temperature=0 时把脚本再跑一遍，回答基本不变。")


# ---------------------------------------------------------------------------
# 2. max_tokens：回答被硬截断
# ---------------------------------------------------------------------------
def max_tokens_demo():
    """max_tokens 是"天花板"不是"目标"：写不下就断在半截。

    用"数数"题演示：输出足够长，必然撞上天花板。
    注意：思考型模型的推理过程也占 max_tokens 额度——额度太小时，
    推理就把预算烧光，正文一个字都来不及输出（content 为空）。
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "请从 1 数到 300，数字之间用空格分隔，不要输出任何其他内容。"}],
        max_tokens=400,  # 故意给得不够：数到 300 远不止 400 token
    )
    choice = response.choices[0]
    print(f"finish_reason = {choice.finish_reason}  ← length 表示被 max_tokens 截断")
    if choice.message.content:
        print(f"实际输出（戛然而止）：{choice.message.content}……")
    else:
        print("实际输出为空：本次推理把 400 的额度烧光了（思考型模型常见，调大再试）")
    print(f"token 用量：{response.usage}")


# ---------------------------------------------------------------------------
# 3. stream=True：逐块打印的打字机效果
# ---------------------------------------------------------------------------
def streaming_demo():
    """流式输出：服务器边生成边推送，客户端边收边打印，首字延迟大幅降低。"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "给我讲一个 100 字左右的冷笑话。"}],
        stream=True,  # 返回值从"完整响应"变成"逐块的迭代器"
    )
    print("【流式输出】", end="", flush=True)
    for chunk in stream:
        # 每个 chunk 只含新增的一小片，delta（增量）里取文本；
        # 开头/结尾的 chunk 可能没有文本（角色标记、结束标记），要判空
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
            time.sleep(0.03)  # 故意放慢一点，让"打字机"效果肉眼可见
    print("\n")


def main():
    print(f"（使用模型：{MODEL}）\n")

    print("===== 1. temperature 对比 =====")
    temperature_demo()

    print("===== 2. max_tokens 截断 =====")
    max_tokens_demo()

    print("\n===== 3. stream 流式输出 =====")
    streaming_demo()


if __name__ == "__main__":
    main()
