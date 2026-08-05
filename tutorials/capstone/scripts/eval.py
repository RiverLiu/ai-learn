"""小评测：5 条问答 + LLM 打分，检验客服 Agent 的端到端质量。

流程：每条问题用全新的 thread_id 跑一遍 Agent（互不干扰）→ 把问题、
参考答案要点、Agent 回答交给 LLM 评委按 1~5 分打分 → 输出评分表与平均分。

运行：uv run tutorials/capstone/scripts/eval.py
"""

import json
import re
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage
from openai import OpenAI

# 脚本直接运行时 sys.path[0] 是 scripts/，补上仓库根目录才能 import tutorials 包
# （scripts → capstone → tutorials → 仓库根，共四级）
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tutorials.capstone.app.agent import get_agent  # noqa: E402
from tutorials.capstone.app.config import load_chat_config  # noqa: E402

# 5 条考题：覆盖价格、功能、隐私三个知识库文档，外加一条退款计算题
EVAL_SET = [
    {
        "id": 1,
        "question": "专业版多少钱？学生有优惠吗？",
        "key_points": "专业版每月 18 元、按年付费每年 168 元；学生凭 edu 邮箱可申请半价，即每月 9 元",
    },
    {
        "id": 2,
        "question": "免费版有什么限制？支持 AI 摘要吗？",
        "key_points": "最多 1000 条笔记、单条最大 2MB、30 天历史版本、2 台设备在线；不包含 AI 摘要",
    },
    {
        "id": 3,
        "question": "我的笔记会被拿去训练 AI 吗？",
        "key_points": "不会用于任何模型训练；AI 摘要按次调用处理文本，处理完成后服务端不保留原文",
    },
    {
        "id": 4,
        "question": "我专业版按年付费，用了 100 天想退款，能退多少？",
        "key_points": "超过 7 天不能全额退；按年付费按剩余月份折算：已用 4 个月、剩余 8 个月，可退 168×8/12=112 元",
    },
    {
        "id": 5,
        "question": "怎么把 Notion 里的笔记迁移过来？",
        "key_points": "设置→导入中选择 Notion，上传 .zip 导出文件；单次导入最多 2GB；保留原始文件夹结构",
    },
]

JUDGE_PROMPT = """你是严格的客服质量评委。根据「问题」「参考答案要点」「客服回答」打分。

评分标准（1~5 的整数）：
5 = 要点全覆盖且事实正确，表达清晰
4 = 基本正确，仅遗漏个别次要要点
3 = 部分正确，遗漏重要要点或表述含混
2 = 大部分错误，只沾到一点边
1 = 答非所问或存在事实错误

只输出 JSON：{"score": <1-5>, "reason": "<一句话理由>"}"""


def run_agent(question: str) -> str:
    """用全新的 thread_id 跑一遍 Agent，返回最终回答文本。"""
    agent = get_agent()
    config = {"configurable": {"thread_id": f"eval-{question[:16]}"}}
    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]}, config=config
    )
    return result["messages"][-1].content


def judge(client: OpenAI, model: str, item: dict, answer: str) -> dict:
    """让 LLM 评委给一条回答打分，返回 {"score": int, "reason": str}。"""
    # 注意：部分模型（如 kimi-k2.6）不支持自定义 temperature，这里不显式设置
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {
                "role": "user",
                "content": (
                    f"问题：{item['question']}\n"
                    f"参考答案要点：{item['key_points']}\n"
                    f"客服回答：{answer}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 评委没有严格输出 JSON 时，从文本里提取第一个 {...}
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            return json.loads(match.group())
        raise


def main():
    print("===== 云雀笔记客服 Agent 评测 =====\n")
    print("首次运行需构建向量索引，请稍候...")
    chat = load_chat_config()
    judge_client = OpenAI(api_key=chat.api_key, base_url=chat.base_url)

    rows = []
    for item in EVAL_SET:
        answer = run_agent(item["question"])
        verdict = judge(judge_client, chat.model, item, answer)
        rows.append((item, answer, verdict))
        print(f"[{item['id']}/{len(EVAL_SET)}] {item['question']} -> {verdict['score']} 分")

    print("\n" + "=" * 72)
    for item, answer, verdict in rows:
        print(f"\n[{item['id']}] {item['question']}  得分：{verdict['score']}/5")
        print(f"  回答：{answer[:120]}{'…' if len(answer) > 120 else ''}")
        print(f"  评委：{verdict['reason']}")

    avg = sum(v["score"] for _, _, v in rows) / len(rows)
    print("\n" + "=" * 72)
    print(f"平均分：{avg:.1f} / 5（{len(rows)} 条）")


if __name__ == "__main__":
    main()
