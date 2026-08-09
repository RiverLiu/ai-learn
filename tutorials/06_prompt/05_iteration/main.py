"""提示词迭代方法论：用数据而不是感觉调提示词。

"我觉得这版提示词更好"不算数。正确的姿势是：
  1. 造一个小评估集：几条有代表性的问题 + 人工给定的标准答案（关键词）；
  2. 每改一版提示词，就让程序对评估集逐条调用、自动打分；
  3. 看得分表决定哪版上线——改提示词从此变成"可度量"的工程活动。

本章场景：为"云雀笔记"客服机器人写提示词。
这套"评估集 + 自动打分"的思路，是后续 evaluation（评估）模块的基础。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置约定：密钥与接口地址走环境变量（或 .env 文件），不写进代码
load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
client = OpenAI()  # 自动读取 OPENAI_API_KEY 与 OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ---------- 业务事实资料（好提示词会用到；坏提示词故意不给） ----------
FACTS = """【事实资料】
- 免费版：0 元，支持 3 台设备，单个附件最大 100MB。
- 专业版：18 元/月，设备数不限，单个附件最大 10GB。
- 团队版：45 元/人/月，含专业版全部功能，另有团队共享空间。
- 售后：所有付费版本支持 7 天无理由退款，在"设置-账户-订单"中自助申请。"""

# ---------- 评估集：5 条问题 + 标准答案关键词（人工给定） ----------
# keywords 是"答对就必须出现"的内容；其中第 3 条考察的是"资料没有就老实说不知道"
EVAL_SET = [
    {"question": "专业版多少钱一个月？", "keywords": ["18元"]},
    {"question": "免费版最多能绑几台设备？", "keywords": ["3台"]},
    {"question": "学生购买有优惠吗？", "keywords": ["不清楚"]},  # 资料未提及，应承认不知道
    {"question": "怎么申请退款？", "keywords": ["7天", "设置"]},
    {"question": "团队版比专业版多了什么？", "keywords": ["共享空间"]},
]

# ---------- 两版提示词 ----------
# v1：凭直觉写的"第一版"——只说了角色，没给资料、没给约束
V1_SYSTEM = "你是云雀笔记的客服助手，请友好地回答用户的问题。"

# v2：按四要素改写——给资料、给约束（没有就说不知道）、给格式
V2_SYSTEM = f"""你是"云雀笔记"的客服专员小云，负责回答价格与售后咨询。

规则：
1. 只能根据下面【事实资料】中的信息回答；
2. 资料中没有提到的内容，一律回答"抱歉，这个我还不清楚"；
3. 回答控制在 3 句话以内。

{FACTS}"""


def compact(text: str) -> str:
    """去掉所有空白字符，避免"18 元"与"18元"这种空格差异造成误判。"""
    return "".join(text.split())


def answer(system_prompt: str, question: str) -> str:
    """用指定提示词回答一个用户问题。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        max_tokens=2000,  # 思考型模型会先消耗推理 token，预算要给足
    )
    return response.choices[0].message.content or ""


def evaluate(version: str, system_prompt: str) -> list[dict]:
    """对一版提示词跑整个评估集，返回每条的命中明细。"""
    results = []
    for item in EVAL_SET:
        reply = answer(system_prompt, item["question"])
        hits = [kw for kw in item["keywords"] if compact(kw) in compact(reply)]
        results.append({
            "version": version,
            "question": item["question"],
            "hits": hits,
            "total": len(item["keywords"]),
            "reply": reply,
        })
    return results


def main():
    # 两版提示词各跑一遍评估集（共 10 次 API 调用）
    all_results = evaluate("v1", V1_SYSTEM) + evaluate("v2", V2_SYSTEM)

    # 打印得分表：问题 × 版本，格子里是"命中关键词数/应命中数"
    print(f"{'问题':24s} {'v1（只给角色）':14s} {'v2（四要素）':14s}")
    print("-" * 58)
    totals = {"v1": [0, 0], "v2": [0, 0]}  # 版本 -> [命中数, 应命中数]
    for item in EVAL_SET:
        row = {"v1": None, "v2": None}
        for r in all_results:
            if r["question"] == item["question"]:
                row[r["version"]] = r
        cells = []
        for v in ("v1", "v2"):
            r = row[v]
            totals[v][0] += len(r["hits"])
            totals[v][1] += r["total"]
            cells.append(f"{len(r['hits'])}/{r['total']}" + (" ✓" if len(r["hits"]) == r["total"] else " ✗"))
        q = item["question"][:12]
        print(f"{q:26s} {cells[0]:16s} {cells[1]:16s}")
    print("-" * 58)
    for v in ("v1", "v2"):
        hit, total = totals[v]
        print(f"{v} 关键词命中率：{hit}/{total} = {hit / total:.0%}")

    # 抽一条最能说明问题的回答做定性对比：资料里没有的"学生优惠"
    print("\n===== 定性对比：'学生购买有优惠吗？' =====")
    for r in all_results:
        if r["question"] == "学生购买有优惠吗？":
            print(f"[{r['version']}] {r['reply']}")

    print("\n===== 小结 =====")
    print("- v1 没有事实资料，模型只能编造价格和功能 → 关键词大量落空。")
    print("- v2 的提升不是'感觉更专业了'，而是命中率从表格里直接读出来。")
    print("- 以后每改一次提示词，先跑一遍评估集再决定要不要上线——这就是提示词迭代。")


if __name__ == "__main__":
    main()
