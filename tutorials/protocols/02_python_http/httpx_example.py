"""
使用 httpx 库发送同步 HTTP 请求。

httpx 是现代的 Python HTTP 客户端，同时支持同步和异步 API，
API 设计与 requests 非常相似。

可通过环境变量 HTTP_BASE_URL 切换测试目标。
"""

import os

import httpx

BASE_URL = os.environ.get("HTTP_BASE_URL", "https://httpbin.org")


def _print_response(name: str, response: httpx.Response):
    """打印响应，非 2xx 时打印文本内容避免 JSON 解析错误。"""
    print(f"[{name}] status: {response.status_code}")
    if response.is_success:
        try:
            data = response.json()
            print(f"  body keys: {list(data.keys())}")
        except ValueError:
            print(f"  text: {response.text[:200]}")
    else:
        print(f"  text: {response.text[:200]}")
    print()


def get_example():
    """发送 GET 请求。"""
    params = {"foo": "bar", "page": 1}
    headers = {"User-Agent": "python-httpx-example/1.0"}

    response = httpx.get(f"{BASE_URL}/get", params=params, headers=headers, timeout=10)
    _print_response("GET /get", response)


def post_json_example():
    """发送 JSON POST 请求。"""
    payload = {"username": "alice", "email": "alice@example.com"}

    response = httpx.post(f"{BASE_URL}/post", json=payload, timeout=10)
    _print_response("POST /post", response)


def client_example():
    """使用 Client 复用连接。"""
    with httpx.Client(base_url=BASE_URL, headers={"User-Agent": "python-httpx-example/1.0"}) as client:
        response1 = client.get("/get", params={"page": 1})
        response2 = client.post("/post", json={"action": "create"})

        _print_response("Client GET /get", response1)
        _print_response("Client POST /post", response2)


if __name__ == "__main__":
    print(f"Using base URL: {BASE_URL}\n")
    get_example()
    post_json_example()
    client_example()
