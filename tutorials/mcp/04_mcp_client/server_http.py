"""HTTP 传输的 MCP Server：与第 1 章相同的工具，从 stdio 换成网络传输。

用法：
    uv run python server_http.py                  # 默认 Streamable HTTP（现行标准）
    uv run python server_http.py sse              # 旧版 SSE 传输（已废弃，演示兼容用）

启动后监听 http://127.0.0.1:8000：
- Streamable HTTP 端点：http://127.0.0.1:8000/mcp
- SSE 端点：http://127.0.0.1:8000/sse
"""

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-mcp-http")


@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """向指定的人问好。"""
    return f"你好，{name}！"


if __name__ == "__main__":
    # 与 stdio 的全部区别就是这一个参数：工具定义、协议消息完全不变
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"
    assert transport in ("sse", "streamable-http"), "用法：python server_http.py [sse|streamable-http]"
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = 8000
    mcp.run(transport=transport)
