"""工具调用（Tool Calling）：让模型操作外部世界。

核心循环与 tutorials/12_mcp/05_llm_agent 一致：
模型决定调用 -> 我们执行 -> 结果回传 -> 模型汇总。LangChain 让每一步更简洁。
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()


# @tool 把函数变成 LangChain 工具：docstring 是给模型看的说明，类型注解生成参数 Schema
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


TOOLS = {t.name: t for t in [get_weather, divide]}


def main():
    model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))
    # bind_tools：把工具 Schema 随请求发给模型，模型返回"想调谁、传什么参"
    model_with_tools = model.bind_tools(list(TOOLS.values()))

    messages = [HumanMessage(content="北京天气怎么样？顺便算一下 10 除以 4")]

    # 工具调用循环：模型可能连续发起多轮调用
    while True:
        ai_message = model_with_tools.invoke(messages)
        messages.append(ai_message)

        # 没有 tool_calls = 模型已给出最终回答
        if not ai_message.tool_calls:
            print(f"最终回答：{ai_message.content}")
            break

        # 逐个执行模型请求的工具调用，结果以 ToolMessage 回传
        for call in ai_message.tool_calls:
            print(f"调用工具 {call['name']}，参数 {call['args']}")
            result = TOOLS[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


if __name__ == "__main__":
    main()
