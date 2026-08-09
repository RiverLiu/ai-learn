# Python 基础教程：json、asyncio、aiohttp

三个主题按"数据 → 并发 → 网络"的顺序排，层层递进：

1. **json**：程序之间交换数据的通用语言。无论是存配置文件还是调 HTTP API，
   你收到的几乎都是 JSON。这是后面一切的基础。
2. **asyncio**：Python 的异步并发模型。当程序大量时间花在"等待"（网络、磁盘）上时，
   异步能让一个线程同时推进成百上千个任务。这是理解现代 Python 网络编程的关键。
3. **aiohttp**：建立在 asyncio 之上的 HTTP 客户端 + 服务器库。
   学会它，就能写出"同时请求一百个 API 也不慢"的程序。

三章都可以离线运行（第 3 章的服务器也由脚本自己启动），直接看输出理解概念。

## 章节目录

1. [01_json](./01_json/)：JSON 与 Python 对象的互相转换、文件读写、常见坑
2. [02_asyncio](./02_asyncio/)：协程、await、并发执行、超时与经典陷阱
3. [03_aiohttp](./03_aiohttp/)：异步 HTTP 客户端与服务器，并发请求实战

## 环境准备

```bash
uv sync   # json、asyncio 是标准库；aiohttp 已包含在项目依赖中
```

运行任意一章：

```bash
uv run tutorials/02_basic/01_json/main.py
```

## 前置与后续

- 前置：只需 Python 基础语法（函数、字典、列表、类的大概概念）。
- 后续：学完可以看 [protocols 教程](../03_protocols/)（HTTP 协议细节）与
  [fastapi 教程](../08_fastapi/)（用框架写生产级 API）。
