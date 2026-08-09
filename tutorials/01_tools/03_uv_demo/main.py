"""一个最小的 uv 项目示例。"""

import requests


def fetch_status(url: str) -> int:
    """获取 URL 的 HTTP 状态码。"""
    response = requests.get(url, timeout=10)
    return response.status_code


def main():
    url = "https://www.example.com"
    status = fetch_status(url)
    print(f"{url} 的状态码是: {status}")


if __name__ == "__main__":
    main()
