"""zero-shot vs few-shot：用示例传递"分类标准"。

任务：把用户留言分类为 咨询 / 投诉 / 夸赞 / 闲聊。
这个任务的难点不在"分类"本身，而在于边界——本公司有两条内部规定：
  规定一：凡涉及退款、取消订阅的留言，无论语气多平静，一律算"投诉"；
  规定二：一条留言既有提问又有不满时，以"投诉"为准。
这些规定模型不可能猜到，唯一的传递办法就是写进提示词。

- zero-shot：只给四个类别名，模型按自己的理解分 → 边界留言分错；
- few-shot：提示词里给 3 个带标注的示例，示例里隐含了内部规定 → 模型照着分。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置约定：密钥与接口地址走环境变量（或 .env 文件），不写进代码
load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
client = OpenAI()  # 自动读取 OPENAI_API_KEY 与 OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ---------- zero-shot 提示词：只有任务，没有示例 ----------
ZERO_SHOT_SYSTEM = (
    "你是客服系统的留言分类器。把用户留言分类为以下四类之一：咨询、投诉、夸赞、闲聊。"
    "只输出类别名，不要输出其他任何内容。"
)

# ---------- few-shot 提示词：同样的任务 + 3 个带标注的示例 ----------
# 注意示例的选择不是随便挑的，每个示例都"暗藏"一条边界规则：
#   示例 2：语气平静地询问退款流程 → 投诉（传递规定一）
#   示例 3：既有提问又有不满 → 投诉（传递规定二）
FEW_SHOT_SYSTEM = ZERO_SHOT_SYSTEM + """

参考以下示例：

留言：请问怎么修改绑定的手机号？
分类：咨询

留言：我想申请退款，请问流程是什么？
分类：投诉

留言：请问怎么导入微信读书的笔记？还有你们最近闪退也太频繁了
分类：投诉"""

# ---------- 测试留言：T1、T2 是踩在规定上的"边界留言" ----------
TESTS = [
    ("T1", "取消订阅的入口在哪里？找了半天没找到，藏得也太深了吧", "投诉"),
    ("T2", "请问怎么把笔记导出成 PDF？另外最近同步老是失败，真的很影响使用", "投诉"),
    ("T3", "这编辑器也太好用了吧，今晚必须加个鸡腿犒劳自己", "夸赞"),
    ("T4", "今天老板又画饼，烦，来记一笔", "闲聊"),
]


def classify(system_prompt: str, message: str) -> str:
    """用指定的 system 提示词给一条留言分类。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"留言：{message}"},
        ],
        # 思考型模型会先消耗推理 token；预算太小可能输出空串，这里留足余量
        max_tokens=1500,
    )
    return (response.choices[0].message.content or "").strip()


def main():
    # 逐条留言分别用 zero-shot 与 few-shot 分类，收集结果后并排打印
    rows = []
    for tid, message, gold in TESTS:
        zero = classify(ZERO_SHOT_SYSTEM, message)
        few = classify(FEW_SHOT_SYSTEM, message)
        rows.append((tid, message, gold, zero, few))

    print(f"{'留言（截断）':22s} {'标准答案':6s} {'zero-shot':10s} {'few-shot':10s}")
    print("-" * 60)
    zero_hits = few_hits = 0
    for tid, message, gold, zero, few in rows:
        zero_ok = zero == gold
        few_ok = few == gold
        zero_hits += zero_ok
        few_hits += few_ok
        short = message[:10] + "…" if len(message) > 10 else message
        print(f"{tid} {short:20s} {gold:8s} {zero:12s} {few:12s} "
              f"{'✓' if zero_ok else '✗'} / {'✓' if few_ok else '✗'}")
    print("-" * 60)
    print(f"命中数：zero-shot {zero_hits}/{len(TESTS)}，few-shot {few_hits}/{len(TESTS)}")

    print("\n===== 小结 =====")
    print("- zero-shot 的错误集中在 T1：它语气平静地在'问入口'，模型按字面分成了咨询——")
    print("  但公司规定涉及取消订阅一律算投诉。不是模型'笨'，是它不知道这条内部规定。")
    print("  （T2 这类'提问+抱怨'的混合留言也在边界上，不同次运行结果可能不同。）")
    print("- few-shot 没有改模型、没有改任务，只用 3 个示例就把'规定'传递给了模型。")
    print("- 示例贵精不贵多：挑能代表边界规则的示例，比堆几十个普通示例更有效。")


if __name__ == "__main__":
    main()
