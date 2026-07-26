"""SSE 与 Streamable HTTP 客户端：通过网络连接 MCP Server。

与 stdio 的区别只在"如何建立传输通道"这一步：
- stdio：Client 启动 Server 子进程，拿到的是读写流；
- HTTP：Server 独立运行（先启动 server_http.py），Client 向 URL 发起连接。

建立通道之后，ClientSession 的用法与 stdio 完全一致——
这正是 MCP"传输与协议解耦"的体现（协议报文见第 6 章，一字不差）。

运行前先在另一个终端启动 Server：
    uv run tutorials/mcp/04_mcp_client/server_http.py            # Streamable HTTP
    uv run tutorials/mcp/04_mcp_client/server_http.py sse        # 旧版 SSE
"""

import asyncio
import sys

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

BASE_URL = "http://127.0.0.1:8000"


async def demo(label: str, url: str, make_transport):
    """建立传输 -> 创建会话 -> 调用工具。对两种 HTTP 传输，这段逻辑一模一样。"""
    print(f"\n===== {label}（{url}） =====")
    # sse_client 产出 (read, write)；streamablehttp_client 多一个 get_session_id，用 *_ 忽略
    async with make_transport(url) as (read, write, *_):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"可用工具：{[t.name for t in tools.tools]}")

            result = await session.call_tool("add", {"a": 19, "b": 23})
            print(f"add(19, 23) = {result.content[0].text}")

            result = await session.call_tool("greet", {"name": "小明"})
            print(f"greet('小明') = {result.content[0].text}")


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "http"
    if mode == "sse":
        await demo("SSE（旧版传输）", f"{BASE_URL}/sse", sse_client)
    else:
        await demo("Streamable HTTP", f"{BASE_URL}/mcp", streamable_http_client)


if __name__ == "__main__":
    asyncio.run(main())
