"""第一次调用 LLM API：消息角色、响应结构、system prompt 的威力。

本章回答三个问题：
1. 怎么用最少的代码让大模型说第一句话？
2. 模型返回的 response 对象里到底有什么？
3. 同一个问题，为什么换个 system prompt，回答风格就完全不同？

运行（在仓库根目录）：uv run tutorials/05_llm_api/01_hello_llm/main.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 向上查找项目根目录的 .env，把里面的变量读进环境变量

# OpenAI() 自动读取环境变量 OPENAI_API_KEY（密钥）和 OPENAI_BASE_URL（服务地址），
# 所以同一份代码不用改动，就能切换 OpenAI 官方、Kimi、DeepSeek 等任何兼容服务。
client = OpenAI()

# 模型名同样走环境变量，没配置时默认 gpt-4o-mini
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ---------------------------------------------------------------------------
# 1. 最小的一次调用：一条 user 消息，拿到模型回答
# ---------------------------------------------------------------------------
def first_call():
    """client.chat.completions.create() 是一切的核心：传入模型名 + 消息列表。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            # messages 是一个列表，每条消息都有 role（角色）和 content（内容）
            {"role": "user", "content": "你好！请用一句话介绍你自己。"},
        ],
    )
    # 回答藏在 response.choices[0].message.content 里。
    # choices 是"候选回答"列表，默认只有 1 个元素，所以永远取 [0]。
    answer = response.choices[0].message.content
    print(f"模型的回答：{answer}")


# ---------------------------------------------------------------------------
# 2. messages 的三种角色：system / user / assistant
# ---------------------------------------------------------------------------
def three_roles():
    """一次请求里可以同时出现三种角色，各管各的事。"""
    messages = [
        # system：给模型立"人设"和规矩，优先级最高，普通用户看不到
        {"role": "system", "content": "你是一个中文助教，回答必须简短，不超过三句话。"},
        # user：用户说的话
        {"role": "user", "content": "什么是 API？"},
        # assistant：模型之前说过的话。多轮对话时要把历史回答原样放回列表，
        # 模型才"记得"自己说过什么（第 3 章展开）。这里先放一条当作上下文示例：
        {"role": "assistant", "content": "API 是程序之间互相调用的约定，像餐厅的点餐窗口。"},
        # 接着上面继续问：
        {"role": "user", "content": "那调用 API 和直接访问网页有什么区别？"},
    ]
    response = client.chat.completions.create(model=MODEL, messages=messages)
    print(f"模型的回答：{response.choices[0].message.content}")


# ---------------------------------------------------------------------------
# 3. 拆解 response：除了回答文本，还有 token 用量等关键信息
# ---------------------------------------------------------------------------
def response_anatomy():
    """真实项目里，usage（token 用量）和 finish_reason（结束原因）几乎必看。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "用一句话解释什么是 token。"}],
    )
    choice = response.choices[0]
    print(f"回答文本 message.content：{choice.message.content}")
    # finish_reason：stop = 正常说完；length = 被 max_tokens 硬截断（第 2 章演示）
    print(f"结束原因 finish_reason：{choice.finish_reason}")
    # usage：本次调用的计费明细。token 是模型的计费单位，中文大约 1 个汉字 ≈ 1~2 个 token
    print(f"token 用量 usage：{response.usage}")
    print(
        f"  输入 {response.usage.prompt_tokens} + 输出 {response.usage.completion_tokens}"
        f" = 总共 {response.usage.total_tokens} token"
    )


# ---------------------------------------------------------------------------
# 4. system prompt 的威力：同一个问题，换"人设"换风格
# ---------------------------------------------------------------------------
def system_prompt_style():
    """system prompt 不改变模型的知识，改变的是它说话的方式。"""
    question = "解释一下什么是递归。"
    personas = [
        "你是一位严谨的计算机系教授，使用专业术语，回答控制在两句话以内。",
        "你是一位幼儿园老师，用 5 岁孩子能听懂的话回答，控制在两句话以内。",
    ]
    for persona in personas:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": persona},  # 只换这一句，其他完全相同
                {"role": "user", "content": question},
            ],
        )
        print(f"【{persona[:12]}…】")
        print(f"  {response.choices[0].message.content}")


def main():
    print(f"（使用模型：{MODEL}）\n")

    print("===== 1. 最小的一次调用 =====")
    first_call()

    print("\n===== 2. 三种角色 =====")
    three_roles()

    print("\n===== 3. 拆解 response =====")
    response_anatomy()

    print("\n===== 4. system prompt 改变风格 =====")
    system_prompt_style()


if __name__ == "__main__":
    main()
