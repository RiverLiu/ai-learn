"""
使用 Python 标准库 http.client 发送 HTTP 请求。

http.client 比 urllib 更底层，接近 socket 编程。
一般不推荐日常使用，但适合理解 HTTP 协议细节。

可通过环境变量 HTTP_BASE_URL 切换测试目标，格式如 http://127.0.0.1:8000。
"""

import json
import os
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

BASE_URL = os.environ.get("HTTP_BASE_URL", "https://httpbin.org")


def _get_connection(path: str):
    """根据 base URL 返回合适的连接对象。"""
    parsed = urlparse(BASE_URL)
    host = parsed.hostname or "httpbin.org"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if parsed.scheme == "https":
        return HTTPSConnection(host, port, timeout=10)
    return HTTPConnection(host, port, timeout=10)


def _parse_json_or_text(body: str) -> dict | str:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body[:200]


def get_example():
    """发送 GET 请求。"""
    parsed = urlparse(BASE_URL)
    conn = _get_connection(BASE_URL)
    conn.request(
        "GET",
        f"{parsed.path}/get?foo=bar&page=1" if parsed.path and parsed.path != "/" else "/get?foo=bar&page=1",
        headers={
            "User-Agent": "python-http-client-example/1.0",
            "Accept": "application/json",
        },
    )

    response = conn.getresponse()
    body = response.read().decode("utf-8")
    print(f"GET status: {response.status} {response.reason}")
    data = _parse_json_or_text(body)
    print(f"body keys: {list(data.keys()) if isinstance(data, dict) else data}")
    print()
    conn.close()


def post_json_example():
    """发送 JSON POST 请求。"""
    payload = json.dumps({"username": "alice", "email": "alice@example.com"})
    parsed = urlparse(BASE_URL)
    path = f"{parsed.path}/post" if parsed.path and parsed.path != "/" else "/post"

    conn = _get_connection(BASE_URL)
    conn.request(
        "POST",
        path,
        body=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "python-http-client-example/1.0",
        },
    )

    response = conn.getresponse()
    body = response.read().decode("utf-8")
    print(f"POST status: {response.status} {response.reason}")
    data = _parse_json_or_text(body)
    print(f"body keys: {list(data.keys()) if isinstance(data, dict) else data}")
    print()
    conn.close()


if __name__ == "__main__":
    print(f"Using base URL: {BASE_URL}\n")
    get_example()
    post_json_example()
