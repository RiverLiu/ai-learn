"""第一个 Deep Agent：看它自己列计划、调工具、写文件。

与 langgraph 教程第 3 章的 ReAct Agent 对比着看：同样的工具、同样的模型，
Deep Agent 会先把任务拆成 todo 清单，过程中把结果写进"文件"，最后汇总——
这就是"深度"的直观含义。

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
        system_prompt="你是一名严谨的调研助手。接到复杂任务先列计划，"
        "重要结论写入文件保存，最后向用户做简短口头总结。",
    )

    task = "调研北京和上海今天的天气，把两城对比摘要写到 /weather_report.md，最后用三句话向我总结。"
    print(f"任务：{task}\n")

    # stream_mode="values"：逐步观察 Agent 的决策（对照 langgraph 教程第 3 章）
    for step in agent.stream({"messages": [HumanMessage(content=task)]}, stream_mode="values"):
        message = step["messages"][-1]
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                print(f"[决策] {call['name']}({call['args']})")
        elif message.type == "tool":
            print(f"[工具] {str(message.content)[:80]}")
        elif message.type == "ai":
            print(f"[回答] {message.content}")

    # 运行结束后检查状态：todos 和 files 是 Deep Agent 的"工作痕迹"
    final = agent.invoke({"messages": [HumanMessage(content=task)]})
    print("\n===== 工作痕迹 =====")
    print(f"todos：{[(t['content'], t['status']) for t in final.get('todos', [])]}")
    print(f"files：{list(final.get('files', {}).keys())}")


if __name__ == "__main__":
    main()
