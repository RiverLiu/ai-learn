"""
使用 Python 标准库 urllib 发送 HTTP 请求。

urllib 是标准库的一部分，无需安装第三方包。
适合了解 HTTP 底层细节，但日常使用不如 requests/httpx 方便。

可通过环境变量 HTTP_BASE_URL 切换测试目标。
"""

import json
import os
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE_URL = os.environ.get("HTTP_BASE_URL", "https://httpbin.org")


def _parse_json_or_text(body: str) -> dict | str:
    """尝试解析 JSON，失败则返回文本。"""
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body[:200]


def get_example():
    """发送 GET 请求。"""
    url = f"{BASE_URL}/get?foo=bar&page=1"
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "python-urllib-example/1.0")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            print(f"GET status: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            data = _parse_json_or_text(body)
            print(f"body keys: {list(data.keys()) if isinstance(data, dict) else data}")
    except HTTPError as e:
        print(f"GET HTTPError: {e.code} {e.reason}")
    print()


def post_json_example():
    """发送 JSON POST 请求。"""
    url = f"{BASE_URL}/post"
    payload = json.dumps({"username": "alice", "email": "alice@example.com"}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "python-urllib-example/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            print(f"POST status: {response.status}")
            data = _parse_json_or_text(body)
            print(f"body keys: {list(data.keys()) if isinstance(data, dict) else data}")
    except HTTPError as e:
        print(f"POST HTTPError: {e.code} {e.reason}")
    print()


def post_form_example():
    """发送表单 POST 请求。"""
    url = f"{BASE_URL}/post"
    payload = urlencode({"username": "alice", "password": "secret"}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            print(f"POST form status: {response.status}")
            data = _parse_json_or_text(body)
            print(f"body keys: {list(data.keys()) if isinstance(data, dict) else data}")
    except HTTPError as e:
        print(f"POST form HTTPError: {e.code} {e.reason}")
    print()


def error_example():
    """处理 HTTP 错误响应。"""
    url = f"{BASE_URL}/status/404"
    req = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(response.read().decode("utf-8"))
    except HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print()


if __name__ == "__main__":
    print(f"Using base URL: {BASE_URL}\n")
    get_example()
    post_json_example()
    post_form_example()
    error_example()
