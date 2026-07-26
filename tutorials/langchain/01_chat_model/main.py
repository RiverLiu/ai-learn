"""与聊天模型对话：消息类型、一次性调用、流式输出。"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()  # 读取 .env（如有）：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME


def get_model() -> ChatOpenAI:
    """创建聊天模型。

    ChatOpenAI 自动读取环境变量 OPENAI_API_KEY 与 OPENAI_BASE_URL，
    因此同一份代码可切换 OpenAI、Kimi 等任何 OpenAI 兼容服务。
    """
    return ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


def main():
    model = get_model()

    # LangChain 用消息对象组织对话：SystemMessage 设定行为，HumanMessage 是用户输入
    messages = [
        SystemMessage(content="你是一个简洁的中文助手，回答不超过两句话。"),
        HumanMessage(content="用一句话解释什么是向量数据库"),
    ]

    # invoke：一次性拿到完整回答，返回 AIMessage
    response = model.invoke(messages)
    print(f"【invoke】{response.content}")
    print(f"  （类型：{type(response).__name__}，token 用量：{response.usage_metadata})")

    # stream：逐段流式输出，聊天界面的标配
    print("【stream】", end="")
    for chunk in model.stream(messages):
        print(chunk.content, end="", flush=True)
    print()

    # batch：并发处理多组输入
    replies = model.batch([
        [HumanMessage(content="1+1=?")],
        [HumanMessage(content="中国的首都是哪里？")],
    ])
    for question, reply in zip(["1+1=?", "中国的首都是哪里？"], replies):
        print(f"【batch】{question} -> {reply.content}")


if __name__ == "__main__":
    main()
