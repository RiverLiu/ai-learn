"""第一个 MCP Server：使用 FastMCP 暴露两个最简单的工具。"""

from mcp.server.fastmcp import FastMCP

# 创建 Server 实例，名称为 "hello-mcp"
mcp = FastMCP("hello-mcp")


@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """向指定的人问好。"""
    return f"你好，{name}！"


if __name__ == "__main__":
    # 默认使用 stdio 传输：由 MCP Client 以子进程方式启动本程序
    mcp.run()
