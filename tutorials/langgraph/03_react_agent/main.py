"""create_react_agent：一行构建工具调用 Agent。

langchain 教程第 5 章手写的"模型提议 -> 执行工具 -> 回传 -> 再提议"循环，
在 LangGraph 里由预建的 ReAct Agent 托管：内部就是一张
"LLM 节点 <-> 工具节点" 的状态图（对照第 2 章的循环）。

需要配置模型（见教程首页）。
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。"""
    fake_db = {"北京": "晴 32°C", "上海": "多云 29°C", "深圳": "雷阵雨 27°C"}
    return fake_db.get(city, f"暂无 {city} 的天气数据")


@tool
def divide(a: float, b: float) -> float:
    """计算 a 除以 b。"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


def main():
    model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))
    # 一行构建 Agent：模型 + 工具，循环、消息管理全部由图托管
    agent = create_agent(model, tools=[get_weather, divide])

    question = "北京和上海的天气怎么样？再算一下 10 除以 4。"
    print(f"问题：{question}\n")

    # stream_mode="values"：每个节点执行完输出一次完整消息列表，逐条打印新消息
    for step in agent.stream(
        {"messages": [HumanMessage(content=question)]}, stream_mode="values"
    ):
        message = step["messages"][-1]
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                print(f"[LLM 决定] 调用 {call['name']}，参数 {call['args']}")
        elif message.type == "tool":
            print(f"[工具返回] {message.content}")
        elif message.type == "ai":
            print(f"[最终回答] {message.content}")


if __name__ == "__main__":
    main()
