"""工具调用（Function Calling）：让模型操作外部世界。

模型本身不会查天气、不会算精确除法——但它可以"请求"我们提供的工具：
    模型：我要调 get_weather("北京")  →  我们的代码本地执行
    →  把结果以 tool 消息回传  →  模型基于结果给出最终回答
这套"请求工具 → 本地执行 → 结果回传 → 再问模型"的循环，就是 Agent 的最小骨架。
后面 mcp 教程的工具协议、langchain 教程的 @tool，全都是对它的封装。

运行（在仓库根目录）：uv run tutorials/llm_api/04_function_calling/main.py
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 向上查找项目根目录 .env
client = OpenAI()  # 自动读取 OPENAI_API_KEY / OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ---------------------------------------------------------------------------
# 1. 定义两个"假工具"：本地普通函数，返回固定数据
# ---------------------------------------------------------------------------
def get_weather(city: str) -> dict:
    """查询天气（假数据）。真实项目里这里会请求和风/高德等天气 API。"""
    fake_db = {
        "北京": {"天气": "晴", "气温": "32℃"},
        "上海": {"天气": "多云转小雨", "气温": "28℃"},
        "广州": {"天气": "雷阵雨", "气温": "30℃"},
    }
    # 查不到的城市也返回一个明确的"错误信息"——对模型来说这只是数据，它会如实转述
    return fake_db.get(city, {"错误": f"没有 {city} 的天气数据"})


def divide(a: float, b: float) -> dict:
    """除法计算器。模型算小数除法经常出错，交给程序最靠谱。"""
    if b == 0:
        return {"错误": "除数不能为 0"}
    return {"结果": a / b}


# ---------------------------------------------------------------------------
# 2. 用 JSON Schema 向模型"登记"工具：名字、用途、参数
# ---------------------------------------------------------------------------
# 模型只看到这段描述（看不到函数实现），description 写得越清楚，调用越准确
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "中国城市名，例如：北京"},
                },
                "required": ["city"],  # 必填参数
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "计算两个数相除（a ÷ b），需要精确计算时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "被除数"},
                    "b": {"type": "number", "description": "除数"},
                },
                "required": ["a", "b"],
            },
        },
    },
]

# 工具名 → 本地函数的映射：模型给出名字，我们查出对应函数来执行
FUNCTION_MAP = {"get_weather": get_weather, "divide": divide}


# ---------------------------------------------------------------------------
# 3. 工具调用循环（本章核心）
# ---------------------------------------------------------------------------
def chat_with_tools(question: str):
    """带着工具与模型对话：可能要来回好几轮，模型才给出最终回答。"""
    print(f"我：{question}")
    messages = [{"role": "user", "content": question}]

    for round_no in range(1, 6):  # 设个上限防死循环（模型异常时可能反复要调工具）
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,  # 把工具清单告诉模型
        )
        message = response.choices[0].message
        # 把模型这条消息原样追加进历史——它可能带着 tool_calls，后面要对应
        messages.append(message)

        if not message.tool_calls:
            # 模型没要工具 → 这就是最终回答，循环结束
            print(f"模型（最终回答）：{message.content}\n")
            return

        # 模型要求调工具：逐个在本地执行，结果以 role="tool" 的消息回传
        for call in message.tool_calls:
            func = FUNCTION_MAP[call.function.name]
            # 模型给的参数是 JSON 字符串，要先解析成 dict
            args = json.loads(call.function.arguments)
            result = func(**args)  # 本地执行真正的函数
            print(f"  [第 {round_no} 轮] 模型请求工具 {call.function.name}({args}) → {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,  # 关键：和模型的调用请求一一对应
                "content": json.dumps(result, ensure_ascii=False),  # content 必须是字符串
            })
        # 循环继续：带着工具结果再问一次模型

    print("超过最大轮数，放弃（正常情况不会到这里）\n")


def main():
    print(f"（使用模型：{MODEL}）\n")

    print("===== 1. 查天气（单次工具调用） =====")
    chat_with_tools("北京今天天气怎么样？适合出门跑步吗？")

    print("===== 2. 算除法（模型不擅长的精确计算） =====")
    chat_with_tools("帮我算一下 100 除以 7，保留两位小数。")

    print("===== 3. 两个问题一起问（模型可能连续或多路调工具） =====")
    chat_with_tools("上海天气如何？顺便算算 22 除以 7 等于多少。")

    print("===== 4. 工具返回错误时（除零） =====")
    chat_with_tools("5 除以 0 等于多少？")


if __name__ == "__main__":
    main()
