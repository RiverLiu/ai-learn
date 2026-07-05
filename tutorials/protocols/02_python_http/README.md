# Python 中使用 HTTP

Python 提供了多种方式进行 HTTP 请求，从标准库到现代异步库都有。

## 示例列表

| 文件 | 说明 |
|------|------|
| `urllib_example.py` | 使用标准库 `urllib` |
| `http_client_example.py` | 使用标准库 `http.client` |
| `requests_example.py` | 使用第三方库 `requests`（最常用） |
| `httpx_example.py` | 使用现代同步/异步库 `httpx` |
| `async_httpx_example.py` | 使用 `httpx` 发送异步请求 |
| `simple_server.py` | 使用标准库启动简单 HTTP 服务器 |

## 运行示例

确保已安装依赖：

```bash
uv sync
```

运行某个示例：

```bash
cd tutorials/protocols/02_python_http
uv run python requests_example.py
```

## 选择建议

- **学习/简单脚本**：`requests`
- **标准库无依赖**：`urllib` 或 `http.client`
- **异步/现代项目**：`httpx`
- **测试 FastAPI**：`httpx` + `TestClient`
