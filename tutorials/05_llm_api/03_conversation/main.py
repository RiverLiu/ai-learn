"""多轮对话：模型没有记忆，"记得"是因为你把历史又发了一遍。

本章三个演示：
1. 两次独立调用 —— 模型完全不记得你上一句说过什么；
2. 把历史消息一起发过去 —— 模型立刻"想起来了"；
3. 一个 5 轮的对话循环 —— 所有聊天产品的最小骨架。

运行（在仓库根目录）：uv run tutorials/05_llm_api/03_conversation/main.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 向上查找项目根目录 .env
client = OpenAI()  # 自动读取 OPENAI_API_KEY / OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def ask(messages: list[dict]) -> str:
    """小工具：发一次请求，返回回答文本。messages 是完整的消息列表。"""
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# 1. 模型没有记忆：两次独立调用，它不知道你的名字
# ---------------------------------------------------------------------------
def no_memory_demo():
    """每次 API 请求互相独立，服务器不保存任何上下文。"""
    # 第 1 次调用：告诉模型你的名字，它礼貌回应
    answer1 = ask([{"role": "user", "content": "请记住：我的名字叫小明。"}])
    print(f"第 1 次调用  我：请记住：我的名字叫小明。")
    print(f"           模型：{answer1}")

    # 第 2 次调用：这是全新的一次请求，和第 1 次毫无关系！
    answer2 = ask([{"role": "user", "content": "我的名字叫什么？"}])
    print(f"第 2 次调用  我：我的名字叫什么？")
    print(f"           模型：{answer2}  ← 它根本不知道")


# ---------------------------------------------------------------------------
# 2. 带上历史再调用：模型"记得"了
# ---------------------------------------------------------------------------
def with_history_demo():
    """所谓"记忆"= 把之前的问答原样塞进 messages 再发一次。"""
    # 先真正问一次，拿到真实回答
    answer1 = ask([{"role": "user", "content": "请记住：我的名字叫小明。"}])

    # 关键：把"我说过的话"（user）和"模型说过的话"（assistant）都放进列表
    messages = [
        {"role": "user", "content": "请记住：我的名字叫小明。"},
        {"role": "assistant", "content": answer1},  # 模型的历史回答也要带上
        {"role": "user", "content": "我的名字叫什么？"},
    ]
    answer2 = ask(messages)
    print(f"带历史调用   我：我的名字叫什么？")
    print(f"           模型：{answer2}  ← 这次它答得出来")


# ---------------------------------------------------------------------------
# 3. 对话循环：聊天产品的最小骨架
# ---------------------------------------------------------------------------
# 预置的 5 轮问题（故意前后指代："这道菜""那"——检验模型是否真在用历史）
QUESTIONS = [
    "我想学做菜，第一道菜你推荐学什么？",
    "这道菜需要准备哪些食材？",
    "我不太能吃辣，可以做不辣的版本吗？",
    "从头到尾大概要花多少时间？",
    "最后用一句话给我打打气吧。",
]


def chat_loop_demo():
    """每轮只做两件事：把"我说的"追加进列表；把"模型说的"也追加进列表。"""
    # system 只放在开头一次，之后每轮都带着它一起发
    messages = [{"role": "system", "content": "你是一位耐心的烹饪老师，回答简短具体，每次不超过三句话。"}]

    for round_no, question in enumerate(QUESTIONS, 1):
        messages.append({"role": "user", "content": question})  # 追加用户消息
        answer = ask(messages)
        messages.append({"role": "assistant", "content": answer})  # 追加模型回答（关键！）

        print(f"第 {round_no} 轮  我：{question}")
        print(f"        老师：{answer}\n")

    print(f"（5 轮下来消息列表已累积 {len(messages)} 条——越聊越长，这就是「上下文」。）")


def main():
    print(f"（使用模型：{MODEL}）\n")

    print("===== 1. 模型没有记忆 =====")
    no_memory_demo()

    print("\n===== 2. 带上历史就「记得」 =====")
    with_history_demo()

    print("\n===== 3. 5 轮对话循环 =====")
    chat_loop_demo()


if __name__ == "__main__":
    main()
