from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


class ConnectionManager:
    """管理 WebSocket 连接。"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    """返回 WebSocket 测试页面。"""
    with open("templates/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = f"客户端 {client_id}: {data}"
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"客户端 {client_id} 已离开")
