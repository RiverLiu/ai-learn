"""interrupt_on：给危险工具加人工审批。

Deep Agent 返回的是 LangGraph 图，langgraph 教程第 4 章的 interrupt 机制原样可用，
且更省事：不用自己画审批节点，interrupt_on 直接给指定工具挂上审批点。

演示：Agent 要写文件 -> 图暂停等待审批 -> 人工批准后写入。

需要配置模型（见教程首页）。
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent

load_dotenv()


def main():
    agent = create_deep_agent(
        model=ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini")),
        tools=[],
        system_prompt="你是写作助手，按用户要求把内容写入指定文件。",
        # 给工具挂审批点：写文件/改文件前必须人工确认
        interrupt_on={"write_file": True, "edit_file": True},
        checkpointer=MemorySaver(),  # 暂停现场靠 checkpointer 保存（同 langgraph 教程）
    )
    config = {"configurable": {"thread_id": "demo-1"}}

    task = "把季度预算 50 万元写入 /budget.md"
    result = agent.invoke({"messages": [HumanMessage(content=task)]}, config=config)

    # 图在 write_file 前暂停：interrupt 载荷里能看到待审批的工具调用
    interrupts = result.get("__interrupt__")
    if not interrupts:
        print(f"未被拦截，直接完成：{result['messages'][-1].content}")
        return

    action = interrupts[0].value["action_requests"][0]
    print(f"图已暂停，等待审批：{action['name']}({action['args']})")

    # 人工批准：resume 传入 decisions 列表，与 action_requests 一一对应
    result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
    print(f"批准之后：{result['messages'][-1].content}")
    print(f"文件已写入：{list(result.get('files', {}).keys())}")

    # 也可以拒绝：{"type": "reject", "message": "理由"}，拒绝原因会作为工具结果回给 Agent


if __name__ == "__main__":
    main()
