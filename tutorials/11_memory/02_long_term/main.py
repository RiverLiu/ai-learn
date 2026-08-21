"""长期记忆闭环：会话结束抽取事实 -> 落盘存储 -> 下次会话注入。

演示两个"会话"（模拟用户两天各聊一次）：
- 会话 1：用户闲聊中透露偏好，结束时 LLM 抽取事实存入 memories.json；
- 会话 2：全新对话，但开场就把存储的事实注入 system prompt——助手"记得"用户。
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

STORE_PATH = Path(__file__).parent / "memories.json"
model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


class Facts(BaseModel):
    """从对话中抽取的、值得长期记住的事实。"""

    facts: list[str] = Field(description="用户的个人信息、偏好、重要约定，每条一句话；闲聊不要")


def extract_facts(history: list[BaseMessage]) -> list[str]:
    """写入环节：让 LLM 从整段对话中筛出值得记的事实（结构化输出）。"""
    transcript = "\n".join(f"{m.type}: {m.content}" for m in history)
    result = model.with_structured_output(Facts).invoke(
        [
            SystemMessage(content="从对话中抽取值得长期记住的用户事实，没有就返回空列表。"),
            HumanMessage(content=transcript),
        ]
    )
    return result.facts


def load_facts() -> list[str]:
    """读取已存储的记忆。"""
    if STORE_PATH.exists():
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))["facts"]
    return []


def save_facts(new_facts: list[str]):
    """存储环节：合并去重后落盘（生产用数据库；更新/遗忘策略见 README）。"""
    facts = sorted(set(load_facts()) | set(new_facts))
    STORE_PATH.write_text(json.dumps({"facts": facts}, ensure_ascii=False, indent=2), encoding="utf-8")


def run_session(questions: list[str]) -> list[BaseMessage]:
    """跑一次会话：开场注入已有记忆，逐轮对话，返回完整历史。"""
    facts = load_facts()
    messages: list[BaseMessage] = [
        SystemMessage(
            content="你是贴心的中文助手。"
            + (f"\n关于这位用户，你记得：{'；'.join(facts)}" if facts else "")
        )
    ]
    print(f"（本会话注入 {len(facts)} 条记忆）")
    for question in questions:
        messages.append(HumanMessage(content=question))
        reply = model.invoke(messages).content
        messages.append(AIMessage(content=reply))
        print(f"用户：{question}\n助手：{reply}")
    return messages


def main():
    print("===== 第一天 =====")
    history = run_session(
        ["我最近减脂，帮我推荐晚餐？", "对了我不吃辣。", "我一般晚上 10 点后才有空锻炼。"]
    )
    facts = extract_facts(history)
    save_facts(facts)
    print(f"\n\n（会话结束，抽取并存储 {len(facts)} 条记忆：{facts}）")

    print("\n===== 第二天（全新会话） =====")
    run_session(["今天吃什么好？", "帮我安排今晚的计划"])


if __name__ == "__main__":
    main()
