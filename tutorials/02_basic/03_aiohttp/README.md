# 03 aiohttp：asyncio 之上的 HTTP

## 为什么是 aiohttp 而不是 requests

`requests.get(...)` 是**同步阻塞**调用：等待响应的那几百毫秒里，线程什么都干不了——
放进 asyncio 程序里就是第 2 章说的"阻塞陷阱"，所有并发任务被它一个人卡住。

aiohttp 的每个请求都是**协程**：等待响应时 `await` 让出执行权，
事件循环同时推进其他请求。实测对比（本章代码会跑出来）：

```
顺序请求 5 个慢接口（各 0.5 秒）：2.5 秒
并发请求 5 个慢接口（各 0.5 秒）：0.5 秒
```

## 客户端：三条铁律

1. **ClientSession 全程复用一个**。Session 管理连接池（TCP 连接复用），
   每个请求新建 Session 等于每次打电话都重新办一张电话卡——慢且浪费。
   用 `async with ClientSession() as session:` 保证用完关闭。
2. **响应用 `async with` 包住**：`async with session.get(url) as resp:`，
   确保连接资源被释放归还给连接池。
3. **读数据都要 `await`**：`await resp.json()`、`await resp.text()`——
   网络数据的读取也是异步的，漏了 await 拿到的是协程对象而不是数据。

常用细节（代码里都有）：

```python
async with session.get(url, params={"city": "北京"}) as resp:  # 查询参数
    if resp.ok:                                  # 状态码 2xx 为 True
        data = await resp.json()                 # 解析 JSON（第 1 章的知识）
async with session.post(url, json={"a": 1}) as resp:  # POST JSON，自动设 Content-Type
ClientSession(timeout=ClientTimeout(total=5))    # 超时：网络请求永远要设
```

## 服务器：顺手认识一下

本章的服务器只有三个零件，看懂它有助于理解"客户端到底在请求什么"：

```python
app = web.Application()
app.router.add_get("/users/{user_id}", get_user)   # 路径参数
runner = web.AppRunner(app); await runner.setup()
await web.TCPSite(runner, "127.0.0.1", 8321).start()
```

处理函数接收 `request`，返回 `web.json_response({...})`（自动序列化 + 设置响应头）。
路径参数用 `request.match_info["user_id"]` 取；读请求体用 `await request.json()`。
（生产环境的 API 开发请直接学 [fastapi 教程](../../08_fastapi/)，aiohttp 服务器了解即可。）

## 运行

```bash
uv run tutorials/02_basic/03_aiohttp/main.py
```

脚本自己启动服务器（8321 端口）、跑完客户端演示后自动关闭。若端口被占用，
改 `main.py` 里的 `PORT` 常量即可。

## 核心概念

- **HTTP 协议细节**（方法、状态码、请求头）不是本章重点，看 [protocols 教程](../../03_protocols/)。
- **并发上限**：真实场景同时发几百个请求时，用 `asyncio.Semaphore` 限流，
  或用 `ClientSession(connector=TCPConnector(limit=50))` 限制连接数。
- 另一个主流选择是 **httpx**（同时支持同步/异步，protocols 教程里有示例）；
  aiohttp 的历史更久、生态更成熟，二者取其一即可。

## 练习建议

1. 给服务器加一个 `GET /users` 返回全部用户列表的接口，再用客户端请求它。
2. 把并发请求数从 5 改成 50，用 `TCPConnector(limit=10)` 限制连接数，观察耗时变化。
3. 给客户端加异常处理：服务器没启动时（先注释掉 `start_server`）会抛什么异常？
