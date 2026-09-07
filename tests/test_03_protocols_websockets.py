import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


MODULE_PATH = Path(__file__).resolve().parents[1] / "tutorials/03_protocols/03_websockets/server.py"
spec = importlib.util.spec_from_file_location("websocket_server", MODULE_PATH)
websocket_server = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(websocket_server)


def test_websocket_echo_returns_client_id_and_message():
    client = TestClient(websocket_server.app)

    with client.websocket_connect("/ws/echo?client_id=tester") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_json()

    assert data == {
        "type": "echo",
        "client_id": "tester",
        "message": "hello",
    }
