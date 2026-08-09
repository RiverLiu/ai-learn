"""
使用 requests 库发送 HTTP 请求。

requests 是 Python 中最流行的 HTTP 库，API 简洁易用。

可通过环境变量 HTTP_BASE_URL 切换测试目标，例如：
    export HTTP_BASE_URL=http://127.0.0.1:8000
"""

import os

import requests

BASE_URL = os.environ.get("HTTP_BASE_URL", "https://httpbin.org")


def _print_response(name: str, response: requests.Response):
    """打印响应，非 2xx 时打印文本内容避免 JSON 解析错误。"""
    print(f"[{name}] status: {response.status_code}")
    if response.ok:
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
    headers = {"User-Agent": "python-requests-example/1.0"}

    response = requests.get(f"{BASE_URL}/get", params=params, headers=headers, timeout=10)
    _print_response("GET /get", response)


def post_json_example():
    """发送 JSON POST 请求。"""
    payload = {"username": "alice", "email": "alice@example.com"}
    headers = {"User-Agent": "python-requests-example/1.0"}

    response = requests.post(
        f"{BASE_URL}/post",
        json=payload,
        headers=headers,
        timeout=10,
    )
    _print_response("POST /post json", response)


def post_form_example():
    """发送表单 POST 请求。"""
    data = {"username": "alice", "password": "secret"}

    response = requests.post(f"{BASE_URL}/post", data=data, timeout=10)
    _print_response("POST /post form", response)


def custom_headers_example():
    """自定义请求头。"""
    headers = {
        "Accept": "application/json",
        "X-Custom-Header": "hello",
    }

    response = requests.get(f"{BASE_URL}/headers", headers=headers, timeout=10)
    _print_response("GET /headers", response)


def error_example():
    """处理 404 错误。"""
    response = requests.get(f"{BASE_URL}/status/404", timeout=10)
    print(f"[GET /status/404] status: {response.status_code}")
    print(f"  is ok: {response.ok}")
    print()


if __name__ == "__main__":
    print(f"Using base URL: {BASE_URL}\n")
    get_example()
    post_json_example()
    post_form_example()
    custom_headers_example()
    error_example()
