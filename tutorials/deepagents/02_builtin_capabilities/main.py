"""解剖内建能力：todos 规划、files 上下文卸载、长系统提示词。

本章任务故意要求 Agent "先写、再读回检查、最后修订"，
逼它把三味药都用一遍；结束后检查状态里的 todos 与 files。

需要配置模型（见教程首页）。
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent

load_dotenv()


def get_weather(city: str) -> str:
    """查询指定城市的实时天气。"""
    fake_db = {"北京": "晴 32°C", "上海": "多云 29°C", "深圳": "雷阵雨 27°C"}
    return fake_db.get(city, f"暂无 {city} 的天气数据")


def main():
    agent = create_deep_agent(
        model=ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini")),
        tools=[get_weather],
        system_prompt="你是严谨的调研助手。写完报告必须读回来检查一遍再修订，确保数字准确。",
    )

    task = "调研北京和上海今天的天气，写入 /report.md；然后读回来检查数字，必要时用编辑功能修订；最后总结。"
    used_tools = set()
    for step in agent.stream({"messages": [HumanMessage(content=task)]}, stream_mode="values"):
        message = step["messages"][-1]
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                used_tools.add(call["name"])
        elif message.type == "ai":
            print(f"[回答] {message.content}")

    final = agent.invoke({"messages": [HumanMessage(content=task)]})

    print("\n===== 1. 规划（write_todos 的产物） =====")
    for todo in final.get("todos", []):
        print(f"  [{todo['status']}] {todo['content']}")

    print("\n===== 2. 文件系统（上下文卸载的产物） =====")
    for path, file in final.get("files", {}).items():
        print(f"  {path}：\n    {file['content'][:100]}...")

    print("\n===== 3. 本次用到的工具（含框架注入的） =====")
    print(f"  {sorted(used_tools)}")


if __name__ == "__main__":
    main()
