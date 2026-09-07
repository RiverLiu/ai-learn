"""WebSocket echo and broadcast demo.

Run from the repository root:
    uv run uvicorn --app-dir tutorials/03_protocols/03_websockets server:app --reload

Or from this directory:
    uv run uvicorn server:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


app = FastAPI(title="WebSocket Protocol Demo")
CURRENT_DIR = Path(__file__).resolve().parent


class ConnectionManager:
    """Track connected clients for the broadcast example."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str) -> None:
        self.active_connections.pop(client_id, None)

    async def broadcast(self, message: dict) -> None:
        stale_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except RuntimeError:
                stale_clients.append(client_id)

        for client_id in stale_clients:
            self.disconnect(client_id)


manager = ConnectionManager()


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse(
        """
        <h1>WebSocket Protocol Demo</h1>
        <p>Open <a href="/client">/client</a> to try the browser client.</p>
        """
    )


@app.get("/client")
def browser_client() -> HTMLResponse:
    html = (CURRENT_DIR / "browser_client.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket, client_id: str = "anonymous") -> None:
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "echo",
                    "client_id": client_id,
                    "message": message,
                }
            )
    except WebSocketDisconnect:
        print(f"echo client disconnected: {client_id}")


@app.websocket("/ws/chat/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str, client_id: str = "anonymous") -> None:
    await manager.connect(client_id, websocket)
    await manager.broadcast(
        {
            "type": "system",
            "room_id": room_id,
            "message": f"{client_id} joined",
        }
    )

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(
                {
                    "type": "chat",
                    "room_id": room_id,
                    "client_id": client_id,
                    "message": message,
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(
            {
                "type": "system",
                "room_id": room_id,
                "message": f"{client_id} left",
            }
        )
