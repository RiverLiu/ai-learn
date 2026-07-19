"""迷你 Agent：让 LLM 通过 function calling 调用 MCP 工具。

工作流程：
1. 连接 MCP Server，把它的工具列表转换为 OpenAI tools 格式；
2. 把用户问题和工具一起发给 LLM；
3. LLM 决定调用工具 → 通过 MCP 执行 → 把结果回传给 LLM；
4. 循环直到 LLM 给出最终回答。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# 连接第 2 章的工具 Server（天气、除法、文件搜索）
SERVER_SCRIPT = Path(__file__).parent.parent / "02_tools" / "server.py"

# 读取 OPENAI_API_KEY；使用第三方兼容服务时同时设置 OPENAI_BASE_URL
llm = OpenAI()
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def to_openai_tools(mcp_tools) -> list[dict]:
    """把 MCP 工具 Schema 转换为 OpenAI function calling 的 tools 格式。"""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,  # MCP 工具本身就用 JSON Schema 描述参数
            },
        }
        for tool in mcp_tools
    ]


async def run_agent(question: str):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = (await session.list_tools()).tools
            tools = to_openai_tools(mcp_tools)
            messages = [{"role": "user", "content": question}]

            # Agent 循环：LLM 可能连续发起多轮工具调用
            while True:
                response = llm.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                )
                message = response.choices[0].message
                messages.append(message)

                # 没有工具调用 = LLM 已给出最终回答
                if not message.tool_calls:
                    print(f"最终回答：{message.content}")
                    break

                # 逐个执行 LLM 请求的工具调用，把结果回传
                for call in message.tool_calls:
                    args = json.loads(call.function.arguments)
                    print(f"调用工具 {call.function.name}，参数 {args}")
                    result = await session.call_tool(call.function.name, args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result.content[0].text,
                        }
                    )


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "北京和上海的天气怎么样？再算一下 10 除以 4。"
    asyncio.run(run_agent(question))
