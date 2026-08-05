"""提示词四要素：角色 / 任务 / 约束 / 输出格式。

"云雀笔记"是一个虚构的笔记软件，模型对它一无所知：
- 坏提示词：随口一问"介绍一下云雀笔记"，模型只能凭空编造（幻觉）；
- 好提示词：用四要素搭好骨架，再附一份事实资料，模型就能"照章回答"——
  资料里有的照实说，资料里没有的老实说"不清楚"。

本章并排打印两份回答，直观感受差距。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置约定：密钥与接口地址走环境变量（或 .env 文件），不写进代码
load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
client = OpenAI()  # 自动读取 OPENAI_API_KEY 与 OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ---------- 坏提示词：一句话，什么要素都没有 ----------
# 这也是真实世界里大多数用户的提问方式：模糊、没有背景、没有格式要求
BAD_QUESTION = "介绍一下云雀笔记"

# ---------- 好提示词：四要素齐备 ----------
# ① 角色：模型以什么身份回答（决定语气和知识边界）
# ② 任务：具体要做什么（越具体越好）
# ③ 约束：什么不能做（这里是防幻觉的关键）
# ④ 输出格式：答案长什么样（方便人读，也方便程序解析）
GOOD_SYSTEM = """你是"云雀笔记"的客服专员小云。
你的任务是回答用户关于产品价格与售后的咨询。

规则：
1. 只能根据下面【事实资料】中的信息回答；
2. 资料中没有提到的内容，一律回答"抱歉，这个我还不清楚"，不要自己推测；
3. 不要编造任何数字、活动或功能。

回答格式要求：
1. 分点列出，每点一句话；
2. 每点末尾用【事实资料】或【客服说明】标注来源；
3. 结尾附一句"还有其他问题欢迎继续提问～"。

【事实资料】
- 免费版：0 元，支持 3 台设备，单个附件最大 100MB。
- 专业版：18 元/月，设备数不限，单个附件最大 10GB。
- 团队版：45 元/人/月，含专业版全部功能，另有团队共享空间。
- 售后：所有付费版本支持 7 天无理由退款，在"设置-账户-订单"中自助申请。"""

# 注意这个问题里埋了一个"陷阱"：事实资料中并没有学生优惠的信息
GOOD_QUESTION = "云雀笔记怎么收费？学生购买有优惠吗？"


def chat(system: str, user: str) -> str:
    """一次最简的 LLM 调用：system 定规矩，user 提问题。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=2500,  # 思考型模型会先消耗推理 token，预算要给足
    )
    return response.choices[0].message.content or ""


def main():
    print("===== 坏提示词：模糊提问 =====")
    print(f"提示词：{BAD_QUESTION}")
    bad_answer = chat("你是一个乐于助人的助手。", BAD_QUESTION)
    print(f"回答：\n{bad_answer}")

    print("\n===== 好提示词：四要素齐备 =====")
    print(f"system 提示词：\n{GOOD_SYSTEM}")
    print(f"\n问题：{GOOD_QUESTION}")
    good_answer = chat(GOOD_SYSTEM, GOOD_QUESTION)
    print(f"回答：\n{good_answer}")

    # 并排对比后的观察重点
    print("\n===== 对比小结 =====")
    print("- 坏提示词：没有资料约束，模型只能自由发挥——要么张冠李戴（把'云雀'联想成'语雀'），")
    print("  要么凭空编造；无论哪种，回答方向都不可控。")
    print("- 好提示词：回答全部来自事实资料，每点标注来源，可追溯、可核对。")
    print("- 关键证据：学生优惠资料里没写——好提示词会老实说'不清楚'，而不是现场编一个折扣。")


if __name__ == "__main__":
    main()
