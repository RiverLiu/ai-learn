"""短期记忆：完整历史 / 滑动窗口 / 摘要压缩三种策略对比。

短期记忆的本质问题：对话越来越长，但上下文窗口（和预算）有限——
每一轮到底把"哪些消息"发给模型？本章手写三种策略，直观对比它们各自
在第 5 轮时还"记不记得"第 1 轮说的名字。

对照：langgraph 教程第 5 章的 checkpointer 负责"存"，本章负责"取多少"。
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


class ChatBot:
    """带短期记忆的聊天机器人，strategy 决定每轮发给模型的消息范围。"""

    def __init__(self, strategy: str, window: int = 4):
        assert strategy in ("full", "window", "summary")
        self.strategy = strategy
        self.window = window
        self.history: list[BaseMessage] = []  # 完整历史永远保留在本地
        self.history.append(SystemMessage(content="回答问题请简短概要"))
        self.summary = ""                     # 仅 summary 策略使用

    def _build_messages(self) -> list[BaseMessage]:
        """三种策略的唯一区别：发给模型的"记忆视野"不同。"""
        if self.strategy == "full":
            return list(self.history)  # 全给：最准但 token 随轮数线性增长
        if self.strategy == "window":
            return list(self.history[-self.window:])  # 只给最近几条：早期信息必然遗忘

        # summary：旧历史压成摘要放 system，外加最近一轮原文
        messages = []
        if self.summary:
            messages.append(SystemMessage(content=f"此前对话摘要：{self.summary}"))
        return messages + list(self.history[-2:])

    def _compress(self):
        """summary 策略：历史超过 4 条时，把较早部分交给 LLM 压缩进摘要。"""
        if len(self.history) <= 4:
            return
        old, self.history = self.history[:-2], self.history[-2:]
        transcript = "\n".join(f"{m.type}: {m.content}" for m in old)
        self.summary = model.invoke(
            [
                SystemMessage(content="把对话压缩成 50 字以内摘要，保留姓名、偏好、约定等关键事实。"),
                HumanMessage(content=f"已有摘要：{self.summary or '（无）'}\n\n新对话：\n{transcript}"),
            ]
        ).content

    def chat(self, text: str) -> str:
        self.history.append(HumanMessage(content=text))
        sent = self._build_messages()
        print(f"  （本轮发给模型 {len(sent)} 条消息）")

        reply = model.invoke(sent).content
        self.history.append(AIMessage(content=reply))
        if self.strategy == "summary":
            self._compress()
        return reply


def demo(strategy: str):
    print(f"\n===== 策略：{strategy} =====")
    bot = ChatBot(strategy)
    script = [
        "我叫小明，在后端团队做 Python 开发。",  # 第 1 轮给出关键信息
        "我最近在学 LangGraph。",
        "推荐一个练手项目？",
        "预算 300 以内的书有推荐吗？",
        "我叫什么名字，是做什么的？",  # 第 5 轮考察第 1 轮的信息
    ]
    for question in script:
        print(f"用户：{question}")
        print(f"助手：{bot.chat(question)}\n{'-' * 30}\n")

    if bot.summary:
        print(f"（最终摘要：{bot.summary}）")


def main():
    for strategy in ("full", "window", "summary"):
        demo(strategy)


if __name__ == "__main__":
    main()
