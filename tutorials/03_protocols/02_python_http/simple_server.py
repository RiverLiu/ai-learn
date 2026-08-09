"""
使用 Python 标准库 http.server 启动一个简单 HTTP 服务器。

这个服务器只用于学习 HTTP 协议，不适合生产环境。

支持路径：
- GET  /get          -> 返回查询参数（模拟 httpbin.org /get）
- POST /post         -> 返回请求体（模拟 httpbin.org /post）
- GET  /headers      -> 返回请求头
- GET  /status/{code}-> 返回指定状态码
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class SimpleHandler(BaseHTTPRequestHandler):
    """简单的 HTTP 请求处理器。"""

    def _send_json(self, status: int, data: dict):
        """发送 JSON 响应。"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self) -> str:
        """读取请求体。"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length:
            return self.rfile.read(content_length).decode("utf-8")
        return ""

    def _headers_dict(self) -> dict:
        """将请求头转为字典。"""
        return {key: value for key, value in self.headers.items()}

    # def do_GET(self):
    #     self.send_response(200)
    #     self.send_header("Content-Type", "application/json")
    #     self.send_header("Cookies", "username=xxx")
    #     self.end_headers()
    #     self.wfile.write(json.dumps({"a": 1}, ensure_ascii=False).encode("utf-8"))
    
    def do_GET(self):
        """处理 GET 请求。"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/get":
            self._send_json(200, {
                "method": "GET",
                "path": self.path,
                "args": {k: v[0] for k, v in parse_qs(parsed.query).items()},
                "headers": self._headers_dict(),
            })
        elif path == "/headers":
            self._send_json(200, {"headers": self._headers_dict()})
        elif path.startswith("/status/"):
            try:
                code = int(path.split("/")[-1])
            except ValueError:
                code = 400
            self._send_json(code, {"status": code})
        elif path == "/":
            self._send_json(200, {"message": "Hello from simple_server.py", "path": self.path})
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        """处理 POST 请求。"""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        if path == "/post":
            content_type = self.headers.get("Content-Type", "")
            parsed_body = body
            if "application/json" in content_type:
                try:
                    parsed_body = json.loads(body)
                except json.JSONDecodeError:
                    pass
            elif "application/x-www-form-urlencoded" in content_type:
                parsed_body = {k: v[0] for k, v in parse_qs(body).items()}

            self._send_json(201, {
                "method": "POST",
                "path": self.path,
                "headers": self._headers_dict(),
                "body": body,
                "json" if isinstance(parsed_body, dict) else "data": parsed_body,
            }
        else:
            self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        """自定义日志输出。"""
        print(f"[{self.date_time_string()}] {format % args}")


def run_server(port: int | None = None):
    """启动服务器。"""
    port = port or int(os.environ.get("PORT", 8000))
    server = HTTPServer(("127.0.0.1", port), SimpleHandler)
    print(f"启动服务器：http://127.0.0.1:{port}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == "__main__":
    run_server()
