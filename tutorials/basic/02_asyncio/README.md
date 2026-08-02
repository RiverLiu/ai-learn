# 02 asyncio：一个线程同时做很多事

## 为什么需要异步

看一组对比（本章代码会真实跑出这个时间差）：

```
顺序下载 3 个文件（各 1 秒）：总耗时 3 秒     —— 等待时间全被浪费
并发下载 3 个文件（各 1 秒）：总耗时 1 秒     —— 等待时被利用
```

程序等待网络/磁盘时，CPU 是闲着的。asyncio 的思路：**等待时把执行权让出来，
先去做别的任务**——不需要多线程，一个线程就能"同时"推进成百上千个 I/O 任务。

## 四个核心概念

- **协程函数**：`async def` 定义的函数。调用它**不会执行**，只是创建一个协程对象。
- **await**：只能在协程里用。意思是"我要等这个结果，等待期间事件循环可以去干别的"。
  真正执行协程、取回返回值，都靠 `await`。
- **事件循环**：调度器。哪个协程在等 I/O、哪个可以继续跑，由它统筹安排。
  程序入口 `asyncio.run(main())` 负责启动和关闭它。
- **任务（Task）**：协程被"丢进"事件循环并发执行的形式。
  `TaskGroup.create_task(...)` 或 `asyncio.gather(...)` 都是在创建任务。

## 并发执行的两种写法

```python
# TaskGroup（Python 3.11+，推荐）：结构清晰，任一任务出错会取消其余任务
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(work("A"))
    t2 = tg.create_task(work("B"))
print(t1.result(), t2.result())   # 出 async with 时已全部完成

# gather（更老更常见）：返回值按传入顺序收集成列表
results = await asyncio.gather(work("A"), work("B"))
```

## 初学者必踩的坑（代码里都有对照实验）

1. **忘记 await**：`say_hello()` 只是创建了协程对象，函数体根本没执行。
   没有"执行"只有"排队等 await"。（静态检查工具会警告 `coroutine was never awaited`。）
2. **在协程里调用阻塞函数**：`time.sleep(1)`、`requests.get(...)` 会把整个线程卡住，
   事件循环停摆，所有"并发"任务排队——并发名存实亡。
   不得已要用同步库时，用 `await asyncio.to_thread(同步函数, ...)` 把它丢到线程池。
3. **混用同步异步入口**：协程只能在协程里被 `await`；同步代码想调用协程，
   唯一入口是 `asyncio.run(...)`，且**只能调用一次**（不能再嵌套调用）。

## 常用工具

- `await asyncio.wait_for(coro, timeout=秒)`：超时抛 `TimeoutError`，网络请求必备。
- `await asyncio.sleep(秒)`：异步等待（本章用它模拟 I/O；真实项目里换成 aiohttp 请求）。
- `asyncio.Semaphore(n)`：限制同时进行的任务数（爬虫限流常用，本教程不展开）。

## 运行

```bash
uv run tutorials/basic/02_asyncio/main.py
```

重点观察：顺序 vs 并发的总耗时对比，以及"直接阻塞"如何把并发打回顺序。

## 练习建议

1. 把 3 个下载任务改成 10 个，耗时不等（0.1～1 秒），观察并发总耗时是否约等于最慢的那个。
2. 用 `asyncio.Semaphore(2)` 限制最多 2 个任务同时下载，总耗时变成多少？为什么？
3. 在 `concurrent_demo` 里故意让"文件B"抛异常，观察 TaskGroup 中其他任务的行为。
