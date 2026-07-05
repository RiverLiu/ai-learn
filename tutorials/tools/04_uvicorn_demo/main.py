"""一个纯 ASGI 应用示例。

不依赖 FastAPI、Starlette 等框架，直接实现 ASGI 接口，
用于理解 Uvicorn 和 ASGI 的基础工作原理。
"""


async def app(scope, receive, send):
    """ASGI 应用入口。

    scope: 包含请求元信息的字典
    receive: 异步函数，用于接收消息
    send: 异步函数，用于发送消息
    """
    if scope["type"] == "http":
        # 获取请求路径和查询参数
        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        # 构造响应内容
        message = f"Hello from pure ASGI! Method: {method}, Path: {path}"
        body = message.encode("utf-8")

        # 发送响应起始行和头部
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/plain; charset=utf-8"],
                [b"content-length", str(len(body)).encode("utf-8")],
            ],
        })

        # 发送响应体
        await send({
            "type": "http.response.body",
            "body": body,
        })
    else:
        # 非 HTTP 请求（如 WebSocket）返回错误
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"text/plain"]],
        })
        await send({
            "type": "http.response.body",
            "body": b"Not Found",
        })
