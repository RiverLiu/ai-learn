"""aiohttp：asyncio 之上的 HTTP 客户端与服务器。

requests 会阻塞线程，与 asyncio 格格不入（第 2 章的"阻塞陷阱"）；
aiohttp 的请求是协程，等待响应时事件循环可以去处理别的任务——
这就是"同时请求一百个 API 也不慢"的秘密。

本章自包含：脚本先在本机 8321 端口启动一个 HTTP 服务器，
再用客户端访问它（最后自动关闭服务器）。全程离线，可放心运行。
"""

import asyncio
import time

from aiohttp import ClientSession, web

HOST, PORT = "127.0.0.1", 8321
BASE = f"http://{HOST}:{PORT}"


# ======================= 服务器部分（先学会被请求，再学请求别人） =======================

USERS = {
    "1": {"name": "小明", "role": "后端工程师"},
    "2": {"name": "小红", "role": "算法工程师"},
}


async def hello(request):
    """GET /hello -> 返回 JSON。"""
    return web.json_response({"message": "你好，aiohttp"})


async def get_user(request):
    """GET /users/{user_id} -> 路径参数 + 404 处理。"""
    user_id = request.match_info["user_id"]
    user = USERS.get(user_id)
    if user is None:
        return web.json_response({"error": f"用户 {user_id} 不存在"}, status=404)
    return web.json_response({"id": user_id, **user})


async def echo(request):
    """POST /echo -> 读取请求体 JSON 并原样返回。"""
    body = await request.json()  # 读请求体也是协程，要 await
    return web.json_response({"received": body})


async def slow(request):
    """GET /slow/{page} -> 模拟耗时 0.5 秒的慢接口，用于并发演示。"""
    await asyncio.sleep(0.5)
    return web.json_response({"page": request.match_info["page"]})


async def start_server() -> web.AppRunner:
    """注册路由并启动服务器，返回 runner（用于最后关闭）。"""
    app = web.Application()
    app.router.add_get("/hello", hello)
    app.router.add_get("/users/{user_id}", get_user)
    app.router.add_post("/echo", echo)
    app.router.add_get("/slow/{page}", slow)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, HOST, PORT).start()
    print(f"服务器已启动：{BASE}\n")
    return runner


# ======================= 客户端部分 =======================


async def client_basics():
    """客户端基本功：GET、POST、状态码、超时。"""
    print("===== 1. 客户端基础 =====")
    # ClientSession 是连接管理器：全程复用一个，不要每个请求新建（原因见 README）
    timeout = aiohttp_timeout()
    async with ClientSession(timeout=timeout) as session:
        # GET：async with 确保响应资源被释放
        async with session.get(f"{BASE}/hello") as resp:
            print(f"GET /hello -> {resp.status} {await resp.json()}")  # resp.json() 也要 await

        # GET 带查询参数：params 自动拼接成 ?city=北京
        async with session.get(f"{BASE}/users/1", params={"lang": "zh"}) as resp:
            print(f"GET /users/1 -> {resp.status} {await resp.json()}")

        # 错误响应：服务器返回 404，用 resp.ok / resp.status 判断
        async with session.get(f"{BASE}/users/999") as resp:
            print(f"GET /users/999 -> {resp.status}（ok={resp.ok}）{await resp.json()}")

        # POST JSON：json= 自动序列化并设置 Content-Type: application/json
        async with session.post(f"{BASE}/echo", json={"name": "小明", "age": 25}) as resp:
            print(f"POST /echo -> {resp.status} {await resp.json()}")


def aiohttp_timeout():
    """统一超时配置：总时长 5 秒。"""
    from aiohttp import ClientTimeout

    return ClientTimeout(total=5)


async def fetch_page(session: ClientSession, page: int) -> dict:
    """请求一次慢接口并返回数据。"""
    async with session.get(f"{BASE}/slow/{page}") as resp:
        return await resp.json()


async def client_concurrent():
    """并发实战：5 个慢请求，顺序要 2.5 秒，并发只要 0.5 秒。"""
    print("\n===== 2. 并发请求（结合第 2 章） =====")
    async with ClientSession() as session:
        # 顺序执行：一个一个等
        start = time.perf_counter()
        for page in range(5):
            await fetch_page(session, page)
        print(f"顺序请求 5 个慢接口：{time.perf_counter() - start:.1f} 秒")

        # 并发执行：等待期间互相利用
        start = time.perf_counter()
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_page(session, page)) for page in range(5)]
        results = [t.result() for t in tasks]
        print(f"并发请求 5 个慢接口：{time.perf_counter() - start:.1f} 秒")
        print(f"结果：{results}")


async def main():
    runner = await start_server()
    try:
        await client_basics()
        await client_concurrent()
    finally:
        await runner.cleanup()  # 优雅关闭服务器
        print("\n服务器已关闭")


if __name__ == "__main__":
    asyncio.run(main())
