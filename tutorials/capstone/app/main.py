"""FastAPI 服务：POST /chat（SSE 流式）+ GET /health。

流式基于 langgraph 的 stream_mode="messages"：LLM 每生成一小段就产出一个
增量块，服务端随即以 SSE 事件推给客户端；工具执行结果也作为独立事件推送，
前端可以据此显示"正在检索知识库…"之类的状态。

运行：uv run uvicorn tutorials.capstone.app.main:app --port 8312
"""

import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from pydantic import BaseModel

from .agent import get_agent

app = FastAPI(title="云雀笔记智能客服", version="1.0.0")


class ChatRequest(BaseModel):
    thread_id: str  # 会话线程 ID：同一 id 共享多轮记忆，换一个 id 即开启新会话
    message: str


def _sse(payload: dict) -> str:
    """把事件编码成一帧 SSE 报文。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _extract_text(content) -> str:
    """消息内容可能是字符串，也可能是内容块列表（多模态格式），统一取出文本。"""
    if isinstance(content, str):
        return content
    return "".join(
        part.get("text", "") for part in content if isinstance(part, dict)
    )


def stream_reply(thread_id: str, message: str) -> Iterator[str]:
    """把 agent 的流式输出转成一个 SSE 事件流（同步生成器，由线程池执行）。"""
    yield _sse({"type": "status", "content": "客服已接入"})
    try:
        agent = get_agent()  # 首次调用要构建向量索引，需几秒
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=message)]}
        for chunk, _metadata in agent.stream(
            inputs, config=config, stream_mode="messages"
        ):
            # 注意：增量块是 AIMessageChunk（type 为类名而非 "ai"），
            # 工具结果是完整 ToolMessage——用 isinstance 区分最稳妥
            if isinstance(chunk, AIMessageChunk):
                # 工具调用块和推理模型的思考块都不带文本，只有 content 块推给前端
                text = _extract_text(chunk.content)
                if text:
                    yield _sse({"type": "token", "content": text})
            elif isinstance(chunk, ToolMessage):
                # 工具执行结果：让前端能展示"客服正在查资料"
                yield _sse(
                    {
                        "type": "tool",
                        "name": chunk.name,
                        "content": _extract_text(chunk.content)[:500],
                    }
                )
        yield _sse({"type": "done"})
    except Exception as exc:
        yield _sse({"type": "error", "message": str(exc)})


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """流式问答：SSE 逐段推送 token / 工具事件，最后以 done 事件结束。"""
    return StreamingResponse(
        stream_reply(request.thread_id, request.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "larknote-support"}
