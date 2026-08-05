"""评估集构建：先有一份固定的考题，"效果有没有变好"才有答案。

流程：加载手工编写的 QA 评估集（data/eval_qa.jsonl）→ 让 LLM 逐条生成回答
（结果缓存到 answers_cache.json，避免重复调用）→ 用最朴素的"关键词命中率"
打分 → 用两个构造好的反例说明：关键词匹配不靠谱，需要更聪明的评估方法（下章）。

运行：uv run tutorials/evaluation/01_eval_dataset/main.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置：优先本章目录下的 .env，其次向上查找（如项目根目录）
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

CHAPTER_DIR = Path(__file__).parent
EVAL_FILE = CHAPTER_DIR / "data" / "eval_qa.jsonl"
CACHE_FILE = CHAPTER_DIR / "answers_cache.json"  # 生成结果缓存（已在 .gitignore 中忽略）
KB_DIR = CHAPTER_DIR.parent.parent / "rag" / "knowledge_base"  # 复用 rag 教程的知识库

client = OpenAI()
CHAT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# 待评估的"系统"：把整份知识库塞进提示词的简易问答（检索质量留到第 3 章单独评估）
SYSTEM_PROMPT = (
    "你是云雀笔记的客服助手。只根据给定资料回答问题，"
    "资料中没有的信息就明说不知道，不要编造。回答要简洁准确。"
)


def load_eval_set(path: Path) -> list[dict]:
    """加载 jsonl 评估集：一行一条 JSON，字段为 question / expected_answer / source / keywords。"""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_knowledge_base(kb_dir: Path) -> str:
    """把知识库全部文档拼成一段资料文本。"""
    return "\n\n".join(
        path.read_text(encoding="utf-8") for path in sorted(kb_dir.glob("*.md"))
    )


def generate_answers(items: list[dict], kb_text: str) -> dict[str, str]:
    """让 LLM 逐条回答评估问题，返回 {question: answer}。

    结果写入缓存文件：评估要反复跑，缓存让指标可复现，也省钱省时间。
    """
    cache: dict[str, str] = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    for item in items:
        question = item["question"]
        if question in cache:
            continue
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"资料：\n{kb_text}\n\n问题：{question}"},
            ],
        )
        cache[question] = response.choices[0].message.content.strip()
        # 逐条落盘：中断后重跑不丢进度
        CACHE_FILE.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  已生成 [{item['id']}/{len(items)}] {question}")

    return cache


def keyword_hits(answer: str, keywords: list[str]) -> list[bool]:
    """检查每个关键词是否出现在回答中，返回逐关键词的命中布尔值。

    匹配前先做归一化：去掉所有空白字符并转小写——否则"30 天"和"30天"、
    "2MB"和"2mb"这种写法差异会把命中率变成纯噪声。
    """
    normalized_answer = "".join(answer.split()).lower()
    return [
        "".join(kw.split()).lower() in normalized_answer for kw in keywords
    ]


def main():
    items = load_eval_set(EVAL_FILE)
    print(f"已加载评估集：{len(items)} 条（{EVAL_FILE.name}）\n")

    print("正在生成回答（已有缓存的条目会跳过）...")
    kb_text = load_knowledge_base(KB_DIR)
    answers = generate_answers(items, kb_text)

    # ---- 朴素指标：关键词命中率 ----
    print("\n===== 关键词命中率 =====")
    total_hits, total_keywords = 0, 0
    for item in items:
        answer = answers[item["question"]]
        hits = keyword_hits(answer, item["keywords"])
        total_hits += sum(hits)
        total_keywords += len(hits)
        marks = "  ".join(
            f"{kw}{'✓' if ok else '✗'}" for kw, ok in zip(item["keywords"], hits)
        )
        print(f"\n[{item['id']}] {item['question']}")
        print(f"  回答：{answer}")
        print(f"  关键词命中：{sum(hits)}/{len(hits)}  {marks}")

    print(f"\n整体关键词命中率：{total_hits}/{total_keywords} = {total_hits / total_keywords:.0%}")

    # ---- 两个构造好的反例：为什么关键词匹配不靠谱 ----
    print("\n===== 关键词匹配为什么不靠谱：两个构造的反例 =====")

    # 反例一（假阳性）：回答事实错误，但关键词一个不少
    wrong_answer = "云雀笔记支持 Windows 和 macOS，暂不支持 iOS 和 Android。"
    hits = keyword_hits(wrong_answer, items[0]["keywords"])
    print(f"\n反例一（答错了却满分）：{wrong_answer}")
    print(f"  问题：{items[0]['question']}  关键词命中：{sum(hits)}/{len(hits)}")

    # 反例二（假阴性）：回答完全正确，只是数字换了个写法
    right_answer = "专业版每月十八元，包年一百六十八元，学生优惠价每月九元。"
    hits = keyword_hits(right_answer, items[1]["keywords"])
    print(f"\n反例二（答对了却零分）：{right_answer}")
    print(f"  问题：{items[1]['question']}  关键词命中：{sum(hits)}/{len(hits)}")

    print("\n结论：关键词只认字面、不认语义——需要能“读懂”答案的评估方法，见 02_llm_judge。")


if __name__ == "__main__":
    main()
