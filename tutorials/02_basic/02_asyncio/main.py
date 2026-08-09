"""asyncio 入门：协程、await、并发执行。

一句话理解 asyncio：程序里大量时间其实在"等待"（等网络、等磁盘），
异步让这些等待时间被利用起来——一个线程就能同时推进成百上千个任务。

本章用 asyncio.sleep 模拟"等待 I/O"（不用真联网），全程离线运行。
"""

import asyncio
import time


# ---------------------------------------------------------------------------
# 1. 第一个协程
# ---------------------------------------------------------------------------
async def say_hello():
    """协程函数：用 async def 定义，里面可以用 await 暂停等待。"""
    print("  你好")
    await asyncio.sleep(0.1)  # await：在这里"让出"执行权，事件循环可以去做别的事
    print("  asyncio！")
    return "返回值也可以有"


# ---------------------------------------------------------------------------
# 2. 顺序执行 vs 并发执行（本章最重要的一组对比）
# ---------------------------------------------------------------------------
async def download(name: str, seconds: float) -> str:
    """模拟一次耗时的下载：seconds 秒都在'等待 I/O'。"""
    print(f"  {name} 开始下载")
    await asyncio.sleep(seconds)  # 假装在下载
    print(f"  {name} 下载完成")
    return f"{name}的内容"


async def sequential_demo():
    """顺序执行：一个等一个，总耗时 = 1+1+1 = 3 秒。"""
    print("【顺序执行】")
    start = time.perf_counter()
    await download("文件A", 1)
    await download("文件B", 1)
    await download("文件C", 1)
    print(f"  总耗时：{time.perf_counter() - start:.1f} 秒\n")


async def concurrent_demo():
    """并发执行：三个任务同时推进，总耗时 ≈ 最长的那个（1 秒）。"""
    print("【并发执行（TaskGroup）】")
    start = time.perf_counter()
    # TaskGroup（Python 3.11+）：把多个协程作为任务同时丢进事件循环
    async with asyncio.TaskGroup() as tg:
        task_a = tg.create_task(download("文件A", 1))
        task_b = tg.create_task(download("文件B", 1))
        task_c = tg.create_task(download("文件C", 1))
    # 出了 async with 时所有任务都已完成，用 task.result() 取返回值
    print(f"  结果：{task_a.result()}, {task_b.result()}, {task_c.result()}")
    print(f"  总耗时：{time.perf_counter() - start:.1f} 秒\n")


async def gather_demo():
    """asyncio.gather：另一种并发写法（更老更常见），返回值按顺序收集成列表。"""
    print("【并发执行（gather）】")
    start = time.perf_counter()
    results = await asyncio.gather(
        download("文件A", 1),
        download("文件B", 0.5),
        download("文件C", 0.2),
    )
    print(f"  结果列表：{results}")
    print(f"  总耗时：{time.perf_counter() - start:.1f} 秒\n")


# ---------------------------------------------------------------------------
# 3. 经典陷阱：阻塞函数会卡住整个事件循环
# ---------------------------------------------------------------------------
def blocking_download(name: str, seconds: float) -> str:
    """错误示范：time.sleep 是同步阻塞，不会'让出'执行权。"""
    time.sleep(seconds)  # 整个线程睡死，事件循环什么都干不了
    return f"{name}的内容"


async def blocking_pitfall():
    """对比：在协程里调用 time.sleep，'并发'名存实亡。"""
    print("【陷阱】并发调用阻塞函数 time.sleep")
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(asyncio.to_thread(blocking_download, "文件A", 1))  # 正确：丢给线程
        # 错误示范放在下面单独对比
    print(f"  to_thread 包装后耗时：{time.perf_counter() - start:.1f} 秒")

    start = time.perf_counter()
    async def bad():
        blocking_download("文件B", 1)  # 直接在协程里阻塞
    async with asyncio.TaskGroup() as tg:
        tg.create_task(bad())
        tg.create_task(bad())  # 两个'并发'任务实际排队执行
    print(f"  直接阻塞的耗时：{time.perf_counter() - start:.1f} 秒（并发失效！）\n")


# ---------------------------------------------------------------------------
# 4. 超时控制：wait_for
# ---------------------------------------------------------------------------
async def timeout_demo():
    """给协程设置时限：超时抛 TimeoutError。"""
    print("【超时控制 wait_for】")
    try:
        await asyncio.wait_for(download("慢文件", 5), timeout=1)
    except TimeoutError:
        print("  超过 1 秒没下完，放弃等待（TimeoutError）\n")


# ---------------------------------------------------------------------------
# 5. 常见错误：忘了 await
# ---------------------------------------------------------------------------
async def forgot_await():
    """调用协程函数而不 await：函数体根本没执行。"""
    print("【陷阱】忘记 await")
    coro = say_hello()  # 只是创建了一个协程对象，什么都不会打印！
    print(f"  say_hello() 得到的是：{type(coro).__name__}（函数体没有执行）")
    result = await coro  # 加上 await 才真正运行
    print(f"  await 之后拿到返回值：{result}")


async def main():
    # asyncio.run(main()) 是程序的异步入口：它启动事件循环，跑完 main 后关闭
    print("===== 1. 第一个协程 =====")
    await say_hello()

    print("\n===== 2. 顺序 vs 并发 =====")
    await sequential_demo()
    await concurrent_demo()
    await gather_demo()

    print("===== 3. 阻塞陷阱 =====")
    await blocking_pitfall()

    print("===== 4. 超时 =====")
    await timeout_demo()

    print("===== 5. 忘记 await =====")
    await forgot_await()


if __name__ == "__main__":
    asyncio.run(main())
