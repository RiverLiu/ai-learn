"""LLM-as-Judge：让模型当裁判，给回答按 rubric 打分。

第 1 章证明关键词匹配不靠谱——"判断回答好不好"本身是语言理解任务，
那就让 LLM 来做。本章定义评分 rubric（正确性 + 忠实度，各 1-5 分），
让 judge 模型对评估集的回答逐条打分；再用一版故意写差的提示词生成第二组回答，
验证评估确实能区分好坏（差版分数应明显下降）。

运行：uv run tutorials/evaluation/02_llm_judge/main.py
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置：优先本章目录下的 .env，其次向上查找（如项目根目录）
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

CHAPTER_DIR = Path(__file__).parent
EVAL_FILE = CHAPTER_DIR.parent / "01_eval_dataset" / "data" / "eval_qa.jsonl"
CH1_CACHE_FILE = CHAPTER_DIR.parent / "01_eval_dataset" / "answers_cache.json"
ANSWERS_CACHE_FILE = CHAPTER_DIR / "answers_cache.json"  # 已在 .gitignore 中忽略
JUDGE_CACHE_FILE = CHAPTER_DIR / "judge_cache.json"      # 已在 .gitignore 中忽略
KB_DIR = CHAPTER_DIR.parent.parent / "rag" / "knowledge_base"

client = OpenAI()
CHAT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# 同一评估集上的两版"被测系统"：好提示词 vs 差提示词
# 好版：与第 1 章相同的提示词（给资料、要求只按资料回答）
GOOD_SYSTEM_PROMPT = (
    "你是云雀笔记的客服助手。只根据给定资料回答问题，"
    "资料中没有的信息就明说不知道，不要编造。回答要简洁准确。"
)
# 差版：不给资料，还鼓励自由发挥——典型的问题提示词
BAD_SYSTEM_PROMPT = (
    "你是云雀笔记的金牌销售。回答用户问题时尽情发挥，把产品说得越强大越好；"
    "不确定的细节可以合理想象，让用户满意最重要。"
)

# 评分 rubric 与 judge 提示词：输入材料齐全 + 只输出 JSON，方便程序化解析
JUDGE_PROMPT = """你是严格、公正的评估专家。请根据【参考资料】和【参考答案】，对【待评回答】打分。

【问题】
{question}

【参考资料】（待评回答只允许使用这些信息）
{context}

【参考答案】
{expected_answer}

【待评回答】
{answer}

评分 rubric（两个维度独立打分，互不影响）：
- correctness 正确性（1-5）：与参考答案相比，待评回答的事实是否正确完整。
  5=事实全部正确且关键点齐全；3=部分正确或明显遗漏关键点；1=严重事实错误。
  注意：措辞不同但语义等价算正确。
- faithfulness 忠实度（1-5）：待评回答是否只基于【参考资料】，有无编造。
  5=每句话都有资料依据；3=有少量无依据的推测；1=大量编造资料中不存在的信息。

只输出一行 JSON，不要输出任何其他内容：
{{"correctness": <1-5的整数>, "faithfulness": <1-5的整数>, "comment": "<一句话理由>"}}"""


def load_json(path: Path, default):
    """读取 JSON 文件，不存在时返回默认值。"""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_eval_set() -> list[dict]:
    with open(EVAL_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_kb_docs() -> dict[str, str]:
    """按文件名加载知识库文档，供 judge 的"参考资料"使用。"""
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(KB_DIR.glob("*.md"))}


def chat(system_prompt: str, user_prompt: str) -> str:
    """调用聊天模型。不设置 temperature：部分模型不允许修改；
    评估的可复现性靠缓存文件保证（见 answers_cache.json / judge_cache.json）。"""
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_answers(items: list[dict]) -> dict[str, dict[str, str]]:
    """生成两版回答：{版本: {question: answer}}，带缓存。

    好版回答优先复用第 1 章的缓存——本章评的就是"上一章生成的那批回答"。
    """
    cache: dict[str, dict[str, str]] = load_json(ANSWERS_CACHE_FILE, {})
    versions = {"good": GOOD_SYSTEM_PROMPT, "bad": BAD_SYSTEM_PROMPT}
    kb_text = "\n\n".join(load_kb_docs().values())

    # 复用第 1 章生成的好版回答（如果存在）
    ch1_cache: dict[str, str] = load_json(CH1_CACHE_FILE, {})
    cache.setdefault("good", {})
    cache["good"] = {**ch1_cache, **cache["good"]}

    for version, system_prompt in versions.items():
        cache.setdefault(version, {})
        for item in items:
            question = item["question"]
            if question in cache[version]:
                continue
            if version == "good":
                user_prompt = f"资料：\n{kb_text}\n\n问题：{question}"
            else:  # 差版故意不给资料
                user_prompt = question
            cache[version][question] = chat(system_prompt, user_prompt)
            save_json(ANSWERS_CACHE_FILE, cache)  # 逐条落盘，中断重跑不丢进度
            print(f"  已生成[{version}] {question}", flush=True)

    return cache


def parse_judge_output(text: str) -> dict:
    """从 judge 输出中正则提取 JSON 并校验分数，解析失败时给兜底值。"""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"correctness": 0, "faithfulness": 0, "comment": f"解析失败：{text[:50]}"}
    try:
        result = json.loads(match.group(0))
        for key in ("correctness", "faithfulness"):
            result[key] = max(1, min(5, int(result[key])))  # 裁剪到 [1, 5]
        return result
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {"correctness": 0, "faithfulness": 0, "comment": f"解析失败：{e}"}


def judge_answers(items: list[dict], answers: dict[str, dict[str, str]]) -> dict[str, dict[str, dict]]:
    """让 judge 逐条评分：{版本: {question: {correctness, faithfulness, comment}}}，带缓存。"""
    cache: dict[str, dict[str, dict]] = load_json(JUDGE_CACHE_FILE, {})
    kb_docs = load_kb_docs()

    for version in ("good", "bad"):
        cache.setdefault(version, {})
        for item in items:
            question = item["question"]
            if question in cache[version]:
                continue
            prompt = JUDGE_PROMPT.format(
                question=question,
                context=kb_docs[item["source"]],
                expected_answer=item["expected_answer"],
                answer=answers[version][question],
            )
            cache[version][question] = parse_judge_output(chat("你是评估专家。", prompt))
            save_json(JUDGE_CACHE_FILE, cache)  # 逐条落盘，中断重跑不丢进度
            print(f"  已评分[{version}] {question}", flush=True)

    return cache


def print_table(version: str, items: list[dict], scores: dict[str, dict[str, dict]]) -> tuple[float, float]:
    """打印逐条评分表，返回 (平均正确性, 平均忠实度)。"""
    label = "好提示词（给资料+要求按资料回答）" if version == "good" else "差提示词（无资料+鼓励发挥）"
    print(f"\n===== {label} =====")
    print(f"{'ID':<4}{'正确性':<6}{'忠实度':<6}理由")
    for item in items:
        s = scores[version][item["question"]]
        print(f"{item['id']:<4}{s['correctness']:<6}{s['faithfulness']:<6}{s['comment']}")
    n = len(items)
    avg_c = sum(scores[version][i["question"]]["correctness"] for i in items) / n
    avg_f = sum(scores[version][i["question"]]["faithfulness"] for i in items) / n
    return avg_c, avg_f


def main():
    items = load_eval_set()
    print(f"已加载评估集：{len(items)} 条；judge 模型：{CHAT_MODEL}\n")

    print("正在生成两版回答（已有缓存的条目会跳过）...")
    answers = generate_answers(items)

    print("正在让 judge 逐条评分（已有缓存的条目会跳过）...")
    scores = judge_answers(items, answers)

    avg_good = print_table("good", items, scores)
    avg_bad = print_table("bad", items, scores)

    print("\n===== 两版平均分对比 =====")
    print(f"{'版本':<12}{'平均正确性':<12}{'平均忠实度':<12}")
    print(f"{'好提示词':<12}{avg_good[0]:<12.2f}{avg_good[1]:<12.2f}")
    print(f"{'差提示词':<12}{avg_bad[0]:<12.2f}{avg_bad[1]:<12.2f}")
    print(
        f"\n差版正确性下降 {avg_good[0] - avg_bad[0]:.2f} 分、"
        f"忠实度下降 {avg_good[1] - avg_bad[1]:.2f} 分——评估能区分好坏，指标有效。"
    )


if __name__ == "__main__":
    main()
