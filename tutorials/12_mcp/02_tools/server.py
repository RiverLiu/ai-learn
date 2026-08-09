"""工具进阶：类型注解、异步、错误处理与结构化输出。"""

import asyncio

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("tools-demo")


class WeatherInfo(BaseModel):
    """天气查询结果（结构化输出）。"""

    city: str = Field(description="城市名")
    condition: str = Field(description="天气状况")
    temperature_celsius: float = Field(description="摄氏温度")


@mcp.tool()
async def get_weather(city: str) -> WeatherInfo:
    """查询指定城市的实时天气（模拟数据）。

    异步工具：适合网络请求、数据库查询等 I/O 操作。
    返回 Pydantic 模型时，SDK 会自动生成输出 Schema，
    Client 可同时拿到人类可读的文本和结构化数据。
    """
    await asyncio.sleep(0.1)  # 模拟网络延迟
    fake_db = {
        "北京": WeatherInfo(city="北京", condition="晴", temperature_celsius=32.0),
        "上海": WeatherInfo(city="上海", condition="多云", temperature_celsius=29.5),
        "深圳": WeatherInfo(city="深圳", condition="雷阵雨", temperature_celsius=27.0),
    }
    if city not in fake_db:
        # 抛出异常：SDK 会将其转为 MCP 协议层的错误返回给 Client
        raise ValueError(f"暂无 {city} 的天气数据")
    return fake_db[city]


@mcp.tool()
def divide(a: float, b: float) -> float:
    """计算 a 除以 b，演示错误处理。"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


@mcp.tool()
def search_files(keyword: str, max_results: int = 5) -> list[str]:
    """根据关键词搜索文件名（模拟），演示默认值参数与列表返回。"""
    all_files = ["report.md", "notes.txt", "todo.list", "main.py", "README.md"]
    matched = [f for f in all_files if keyword.lower() in f.lower()]
    return matched[:max_results]


if __name__ == "__main__":
    mcp.run()
