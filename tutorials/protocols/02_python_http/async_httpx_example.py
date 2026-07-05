"""
使用 httpx 发送异步 HTTP 请求。

异步请求适合高并发场景，例如同时请求多个 API。

可通过环境变量 HTTP_BASE_URL 切换测试目标。
"""

import asyncio
import os

import httpx

BASE_URL = os.environ.get("HTTP_BASE_URL", "https://httpbin.org")


def _safe_json(response: httpx.Response):
    """安全解析 JSON。"""
    if response.is_success:
        try:
            return response.json()
        except ValueError:
            return response.text[:200]
    return response.text[:200]


async def fetch_get(client: httpx.AsyncClient):
    """发送 GET 请求。"""
    response = await client.get("/get", params={"foo": "bar"}, timeout=10)
    print(f"[async GET /get] status: {response.status_code}")
    return _safe_json(response)


async def fetch_post(client: httpx.AsyncClient):
    """发送 POST 请求。"""
    response = await client.post(
        "/post",
        json={"username": "alice"},
        timeout=10,
    )
    print(f"[async POST /post] status: {response.status_code}")
    return _safe_json(response)


async def main():
    """并发发送多个异步请求。"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        results = await asyncio.gather(
            fetch_get(client),
            fetch_post(client),
        )

    print(f"GET result: {results[0]}")
    print(f"POST result: {results[1]}")


if __name__ == "__main__":
    print(f"Using base URL: {BASE_URL}\n")
    asyncio.run(main())
