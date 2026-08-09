"""SSE（Server-Sent Events）流式输出：让 AI 回答像打字机一样逐段到达。

与第 10 章 WebSocket 对比：SSE 是服务器到浏览器的单向推送，基于普通 HTTP，
更轻量、自动重连——AI 应用的"流式回答"几乎都用它。

运行：uv run uvicorn main:app --reload
然后 curl -N "http://127.0.0.1:8000/chat?message=讲个笑话" 或浏览器打开 http://127.0.0.1:8000
"""

import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from openai import OpenAI

load_dotenv()  # 读取 .env：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME

app = FastAPI(title="SSE 流式输出")
client = OpenAI()
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


def sse(data: str) -> str:
    """SSE 协议格式：每条消息以 'data: ' 开头、两个换行结尾。"""
    return f"data: {data}\n\n"


def chat_stream(message: str) -> Generator[str, None, None]:
    """同步生成器：StreamingResponse 会把它放到线程池执行，
    因此这里用同步的 openai 客户端不会阻塞事件循环（新手常踩的坑）。"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": message}],
        stream=True,  # 关键参数：让模型边生成边返回
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content  # 每个 chunk 只含一小段增量文本
        if delta:
            yield sse(delta.replace("\n", "\\n"))  # SSE 消息内不能有真实换行
    yield sse("[DONE]")


@app.get("/chat")
def chat(message: str = "用三句话介绍什么是 SSE"):
    """SSE 端点：Content-Type 必须是 text/event-stream。"""
    return StreamingResponse(
        chat_stream(message),
        media_type="text/event-stream",
        # 经过 nginx 等反向代理时需要下面这个头禁用缓冲，否则前端收不到实时流
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@app.get("/")
def index():
    """浏览器演示页（EventSource 是 SSE 的浏览器原生 API）。"""
    return FileResponse(Path(__file__).parent / "templates" / "index.html")
