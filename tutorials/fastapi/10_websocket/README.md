# 10 WebSocket

实现实时双向通信。

## 运行

```bash
cd tutorials/fastapi/10_websocket
uv run uvicorn main:app --reload
```

## 测试

打开浏览器访问 http://127.0.0.1:8000/，打开多个标签页即可体验聊天室。

## 知识点

- `@app.websocket("/ws/{client_id}")` 声明 WebSocket 路由
- `WebSocket` 对象：`accept`、`receive_text`、`send_text`
- `WebSocketDisconnect` 处理客户端断开
- 使用连接管理器实现广播
- WebSocket 与 HTTP 的区别：全双工、长连接
