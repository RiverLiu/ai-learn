"""用 Python 编写 MCP Client：连接第 1 章的 Server，列出并调用工具。"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 要连接的 Server 脚本（第 1 章的 hello-mcp）
SERVER_SCRIPT = Path(__file__).parent.parent / "01_hello_mcp" / "server.py"


async def main():
    # 指定如何启动 Server：以子进程方式运行，通过 stdio 通信
    server_params = StdioServerParameters(
        command=sys.executable,  # 当前虚拟环境的 Python
        args=[str(SERVER_SCRIPT)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接：协商协议版本、交换能力声明
            await session.initialize()

            # 列出 Server 提供的所有工具
            tools = await session.list_tools()
            print("可用工具：")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 调用 add 工具
            result = await session.call_tool("add", {"a": 19, "b": 23})
            print(f"\nadd(19, 23) = {result.content[0].text}")

            # 调用 greet 工具
            result = await session.call_tool("greet", {"name": "小明"})
            print(f"greet('小明') = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
