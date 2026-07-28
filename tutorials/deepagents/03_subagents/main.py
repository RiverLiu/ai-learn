"""子代理：把子任务派给独立上下文的子代理，主代理只收结论。

主代理通过内建的 task 工具调用子代理。子代理有自己独立的消息历史
（上下文隔离），只把最终结论返回给主代理——避免子任务的海量中间过程
污染主上下文。这正是一个"研究主管带团队"的模式。

需要配置模型（见教程首页）。
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent

load_dotenv()


def search_pricing(plan: str) -> str:
    """查询云雀笔记某个价格方案的详情。"""
    fake_db = {
        "免费版": "1000 条笔记上限，30 天历史版本，2 台设备",
        "专业版": "每月 18 元，无限笔记，完整历史，10 台设备，每月 500 次 AI 摘要",
        "团队版": "每成员每月 45 元，5 人起购，含权限管理与 SSO",
    }
    return fake_db.get(plan, f"没有名为 {plan} 的方案")


# 子代理用普通 dict 声明：名字、职责描述（主代理据此决定何时派单）、提示词、可用工具
RESEARCHER = {
    "name": "researcher",
    "description": "资料调研员，负责查找云雀笔记各价格方案的准确信息",
    "system_prompt": "你是调研员。只用 search_pricing 工具获取事实，逐条列出，不要编造。",
    "tools": [search_pricing],
}

CRITIC = {
    "name": "critic",
    "description": "审校专家，负责检查报告中的事实错误与遗漏",
    "system_prompt": "你是审校专家。检查报告中的价格、数字、权益描述是否准确完整，"
    "逐条给出'通过'或修改意见。",
}


def main():
    agent = create_deep_agent(
        model=ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini")),
        tools=[],  # 主代理自己没有查询工具——必须派单给 researcher
        system_prompt="你是研究主管。流程：派 researcher 调研 -> 亲自把报告写入 /report.md "
        "-> 派 critic 审校 -> 按意见修订 -> 向用户总结。",
        subagents=[RESEARCHER, CRITIC],
    )

    task = "写一份云雀笔记三个价格方案的对比报告，经审校修订后总结要点。"
    for step in agent.stream({"messages": [HumanMessage(content=task)]}, stream_mode="values"):
        message = step["messages"][-1]
        if message.type == "ai" and message.tool_calls:
            for call in message.tool_calls:
                if call["name"] == "task":
                    # task 工具的参数里有子代理类型与任务描述
                    print(f"[派单] -> {call['args'].get('subagent_type')}：{call['args'].get('description')}")
                else:
                    print(f"[决策] {call['name']}")
        elif message.type == "ai":
            print(f"[回答] {message.content}")


if __name__ == "__main__":
    main()
