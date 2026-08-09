# Uvicorn 示例：纯 ASGI 应用

这个示例展示了一个不依赖任何 Web 框架的纯 ASGI 应用，帮助你理解 Uvicorn 和 ASGI 的基础。

## 文件说明

- `main.py`：定义了一个名为 `app` 的 ASGI 应用

## 运行

### 1. 进入示例目录

```bash
cd tutorials/01_tools/04_uvicorn_demo
```

### 2. 启动服务器

使用 `uv run` 自动调用项目虚拟环境中的 uvicorn：

```bash
uv run uvicorn main:app --reload
```

或者先激活虚拟环境，再直接运行：

```bash
source ../../.venv/bin/activate
uvicorn main:app --reload
```

### 3. 访问

```bash
curl http://127.0.0.1:8000/
```

预期输出：

```
Hello from pure ASGI! Method: GET, Path: /
```

### 4. 尝试其他路径

```bash
curl http://127.0.0.1:8000/hello?foo=bar
```

输出会显示请求方法和路径：

```
Hello from pure ASGI! Method: GET, Path: /hello
```

## 常用命令

以下命令默认使用 `uv run` 前缀。如果已激活虚拟环境，可以省略 `uv run`。

```bash
# 指定端口
uv run uvicorn main:app --port 8080

# 监听所有网络接口（适合局域网测试）
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# 生产环境多进程
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 停止

按 `Ctrl+C` 停止服务器。

## 练习

1. 修改 `main.py`，让它返回 JSON 而不是纯文本
2. 尝试解析查询参数并返回
3. 把 `app` 改名为 `application`，并用 `uvicorn main:application` 启动
