"""思维链（Chain-of-Thought）：先推理，后答案，再自我检查。

三道带陷阱的小学数学题（单位换算、隐藏条件），对比三种提示词：
- 坏提示词："直接给出答案，不要过程" —— 答案无法审计，错了也无从察觉；
- 好提示词："先列出推理过程，再给出最终答案" —— 每一步都能检查；
- 更好：再加一句"把答案代回题目自我检查一遍" —— 让模型自己抓自己的错误。

诚实的预期：本章默认使用思考型模型（如 kimi-k2.6），它把推理"藏"在内部
（reasoning tokens），三种提示词可能全部答对——这恰恰说明"模型越强，
提示词差异越小，但方法通用"。在非思考型模型上差异是决定性的：
实测 moonshot-v1-8k 直接答 3 题全错，思维链 3 题全对（数据见本章 README）。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置约定：密钥与接口地址走环境变量（或 .env 文件），不写进代码
load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
client = OpenAI()  # 自动读取 OPENAI_API_KEY 与 OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ---------- 三道陷阱题 ----------
# 每题都埋了坑：单位换算、隐藏条件（段数-1、倒推、"盈亏"），
# gold 是评判用的标准答案关键词（出现在答案里即算命中）
PROBLEMS = [
    {
        "question": "一根 4.2 米长的木料，要锯成 70 厘米长的小段。"
                    "每锯一次需要 1 分 30 秒。把这根木料全部锯完，一共需要多少秒？",
        "gold": ["450"],
        "trap": "4.2 米=420 厘米→6 段；6 段只需锯 5 次（段数-1）；1 分 30 秒=90 秒；5×90=450 秒",
    },
    {
        "question": "一筐鸡蛋，第一天卖出总数的一半多 10 个，第二天卖出剩下的一半多 5 个，"
                    "这时还剩 20 个。这筐鸡蛋原来有多少个？",
        "gold": ["120"],
        "trap": "倒推：第二天卖前有 (20+5)×2=50 个；原来有 (50+10)×2=120 个",
    },
    {
        "question": "同学们分苹果，每人分 5 个则多 12 个，每人分 7 个则少 6 个。"
                    "一共有多少名同学？一共有多少个苹果？",
        "gold": ["9", "57"],
        "trap": "盈亏问题：人数 (12+6)÷(7-5)=9 名；苹果 5×9+12=57 个",
    },
]

# ---------- 三种提示词 ----------
DIRECT_PROMPT = "请直接给出最终答案，不要写任何计算过程，只输出答案本身。"
COT_PROMPT = "请一步步分析：先列出推理过程（特别注意单位换算和隐藏条件），再给出最终答案。"
COT_CHECK_PROMPT = (
    COT_PROMPT + "给出答案后，再把答案代回题目重新验算一遍，确认无误后输出最终结果。"
)


def ask(prompt: str, question: str, max_tokens: int) -> str:
    """用指定提示词问一道题。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        # 思考型模型会先消耗推理 token，思维链/自查的输出也更长，预算要逐级给足
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def hit(answer: str, gold: list[str]) -> bool:
    """标准答案关键词全部出现在回答里，记为命中（粗糙但够用，系统化的自动评分见第 5 章）。"""
    return all(g in answer for g in gold)


def main():
    styles = [
        ("直接答（坏）", DIRECT_PROMPT, 1000),
        ("先推理后答案（好）", COT_PROMPT, 3000),
        ("推理+自我检查（更好）", COT_CHECK_PROMPT, 5000),
    ]
    # scoreboard[提示词] = [是否命中, ...]
    scoreboard: dict[str, list[bool]] = {name: [] for name, _, _ in styles}

    for i, prob in enumerate(PROBLEMS, 1):
        print(f"===== 第 {i} 题 =====")
        print(f"题目：{prob['question']}")
        print(f"（陷阱：{prob['trap']}）")
        for name, prompt, max_tokens in styles:
            answer = ask(prompt, prob["question"], max_tokens)
            ok = hit(answer, prob["gold"])
            scoreboard[name].append(ok)
            print(f"\n--- {name} [{'✓ 命中' if ok else '✗ 未命中'}] ---")
            print(answer)
        print()

    # 得分表：同一套题 × 三种提示词
    print("===== 得分表 =====")
    header = f"{'提示词':22s}" + "".join(f"第{i}题  " for i in range(1, len(PROBLEMS) + 1)) + "合计"
    print(header)
    print("-" * 56)
    for name, _, _ in styles:
        marks = scoreboard[name]
        cells = "".join(f"{'✓' if m else '✗'}     " for m in marks)
        print(f"{name:24s}{cells}{sum(marks)}/{len(marks)}")

    print("\n===== 小结 =====")
    print("- 如果三种提示词全对（思考型模型的常见结果）：别急着说方法没用——")
    print("  模型只是把推理藏进了内部。但'直接答'的答案你无法审计，")
    print("  它说 450，你不知道它有没有踩中'段数-1'的陷阱。")
    print("- 换非思考型模型（如 moonshot-v1-8k）重跑本章，差异立刻现形：")
    print("  实测直接答 3 题全错，先推理后答案 3 题全对。")
    print("- 自我检查让模型把答案代回题目验算，是抓残余错误的第二道保险。")


if __name__ == "__main__":
    main()
