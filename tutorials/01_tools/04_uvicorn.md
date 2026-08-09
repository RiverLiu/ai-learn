# Uvicorn：ASGI Web 服务器

## Uvicorn 是什么

[Uvicorn](https://www.uvicorn.org/) 是一个基于 [uvloop](https://github.com/MagicStack/uvloop) 和 [httptools](https://github.com/MagicStack/httptools) 构建的**高性能 ASGI Web 服务器**，使用 Python 编写。

它的核心作用：**运行 ASGI 应用**，让 Python 异步 Web 框架能够处理 HTTP 请求。

## 什么是 ASGI

ASGI（Asynchronous Server Gateway Interface，异步服务器网关接口）是 Python 异步 Web 应用和服务器之间的标准接口。

与 WSGI（如 Flask、Django 早期使用的接口）相比，ASGI 支持：

- 异步请求处理
- WebSocket
- HTTP/2
- 长连接和后台任务

常见 ASGI 框架：

- **FastAPI**
- **Starlette**
- **Django Channels**
- **Quart**
- **Sanic**

## 为什么需要 Uvicorn

Python 异步框架（如 FastAPI）本身不是独立服务器，需要一个 ASGI 服务器来：

- 监听网络端口
- 解析 HTTP 请求
- 将请求交给 ASGI 应用处理
- 返回响应给客户端

Uvicorn 就是做这个工作的，它类似于：

- WSGI 世界里的 **Gunicorn** / **uWSGI**
- Node.js 世界里的 **Node 运行时**
- Go 世界里的 **net/http**

## 安装

Uvicorn 已经包含在本项目的依赖中。如果单独安装：

```bash
pip install uvicorn

# 推荐安装标准依赖（包含 uvloop、httptools、websockets 等性能优化）
pip install "uvicorn[standard]"
```

使用 uv：

```bash
uv add uvicorn
# 或
uv add "uvicorn[standard]"
```

## 基本用法

假设你有一个 ASGI 应用文件 `main.py`，其中定义了名为 `app` 的 ASGI 实例：

```python
# main.py
async def app(scope, receive, send):
    assert scope["type"] == "http"
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/plain"]],
    })
    await send({
        "type": "http.response.body",
        "body": b"Hello, Uvicorn!",
    })
```

启动：

```bash
uvicorn main:app
```

默认监听 `127.0.0.1:8000`。

## 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--host` | 绑定主机 | `--host 0.0.0.0` |
| `--port` | 绑定端口 | `--port 8080` |
| `--reload` | 开发模式，代码修改后自动重启 | `--reload` |
| `--workers` | 工作进程数（生产环境） | `--workers 4` |
| `--log-level` | 日志级别 | `--log-level info` |
| `--ssl-keyfile` | SSL 私钥路径 | `--ssl-keyfile key.pem` |
| `--ssl-certfile` | SSL 证书路径 | `--ssl-certfile cert.pem` |

### 开发模式

```bash
uvicorn main:app --reload
```

### 指定主机和端口

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 生产环境多进程

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 与 FastAPI 一起使用

FastAPI 应用本身就是 ASGI 应用，启动方式完全相同：

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
```

```bash
uvicorn main:app --reload
```

## Uvicorn + Gunicorn

Gunicorn 是 WSGI 服务器，但可以通过 worker 类来管理多个 Uvicorn 进程：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

这种方式适合生产环境，因为：

- Gunicorn 负责进程管理
- Uvicorn 负责处理 ASGI 请求
- 可以平滑重启、管理 worker 生命周期

## 示例：纯 ASGI 应用

见 `tutorials/01_tools/04_uvicorn_demo/`，展示了一个不依赖任何框架的纯 ASGI 应用。

## 开发 vs 生产

| 场景 | 推荐命令 |
|------|---------|
| 本地开发 | `uvicorn main:app --reload` |
| 简单部署 | `uvicorn main:app --host 0.0.0.0 --port 8000` |
| 生产多进程 | `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker` |

## 常见问题

### 1. `main:app` 是什么意思？

`main:app` 表示：在 `main.py` 文件中，找到名为 `app` 的 ASGI 应用实例。

### 2. 为什么开发模式用 `--reload`，生产不能用？

`--reload` 会监控文件变化并重启服务，方便开发，但会带来性能开销和稳定性问题，不适合生产。

### 3. Uvicorn 支持 HTTPS 吗？

支持：

```bash
uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

生产环境通常在前置反向代理（Nginx/Caddy）上处理 HTTPS。

### 4. 为什么启动 FastAPI 时日志显示 `Uvicorn running on ...`？

因为 FastAPI 本身没有内置服务器，当你运行 `uvicorn main:app` 时，实际运行的是 Uvicorn 服务器，FastAPI 作为 ASGI 应用被加载。
