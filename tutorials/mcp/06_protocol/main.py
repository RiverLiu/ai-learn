"""MCP 协议细节：绕过 SDK，手写 JSON-RPC 2.0 与 Server 对话。

MCP 的秘密在于它一点也不神秘：stdio 传输就是"每行一条 JSON 消息"。
本脚本不 import 任何 mcp 库，用 subprocess + 手写 JSON 完成完整生命周期：
initialize 握手 -> initialized 通知 -> tools/list -> tools/call -> 错误演示 -> ping。

连接的是第 2 章的 Server（工具有结构化输出、会抛错，适合演示协议细节）。
"""

import asyncio
import json
import sys
from pathlib import Path

SERVER_SCRIPT = Path(__file__).parent.parent / "02_tools" / "server.py"


class RawMcpClient:
    """最小 MCP 客户端：直接向 Server 子进程的 stdin/stdout 读写 JSON 行。"""

    def __init__(self, proc):
        self.proc = proc
        self.next_id = 0

    async def send(self, message: dict):
        line = json.dumps(message)  # stdio 传输：一条消息一行 JSON，换行分隔
        print(f"--> {json.dumps(message, ensure_ascii=False)}")
        self.proc.stdin.write(line.encode() + b"\n")
        await self.proc.stdin.drain()

    async def recv(self) -> dict:
        line = await self.proc.stdout.readline()
        message = json.loads(line)
        print(f"<-- {json.dumps(message, ensure_ascii=False)}")
        return message

    async def request(self, method: str, params: dict | None = None) -> dict:
        """JSON-RPC 请求：带 id，Server 必须回一条同 id 的响应。"""
        self.next_id += 1
        await self.send({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}})
        return await self.recv()

    async def notify(self, method: str, params: dict | None = None):
        """JSON-RPC 通知：不带 id，Server 不会也不应回复。"""
        await self.send({"jsonrpc": "2.0", "method": method, "params": params or {}})


async def main():
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(SERVER_SCRIPT),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,  # 协议走 stdout；FastMCP 的日志走 stderr，互不污染
    )
    client = RawMcpClient(proc)

    print("【1】initialize 握手：客户端提议协议版本、声明能力；Server 应答确认")
    await client.request(
        "initialize",
        {
            "protocolVersion": "2025-06-18",  # 客户端支持的最新版本；不兼容时 Server 会报错并给出它支持的版本
            "capabilities": {},  # 客户端能力（roots/sampling/elicitation），本例不声明
            "clientInfo": {"name": "raw-jsonrpc-client", "version": "0.1.0"},
        },
    )

    print("\n【2】initialized 通知：握手完成，进入正常通信阶段（此后才允许发其他请求）")
    await client.notify("notifications/initialized")

    print("\n【3】tools/list：发现工具（注意 inputSchema/outputSchema 就在响应里）")
    await client.request("tools/list")

    print("\n【4】tools/call 正常调用：返回 content（文本块）+ structuredContent（结构化数据）")
    await client.request("tools/call", {"name": "get_weather", "arguments": {"city": "北京"}})

    print("\n【5】工具内部抛错：协议层仍是 result，但 isError=true——工具错误不是协议错误")
    await client.request("tools/call", {"name": "divide", "arguments": {"a": 1, "b": 0}})

    print("\n【6】调用不存在的工具：本 SDK 同样按工具级错误处理（isError=true），LLM 可读到原因")
    await client.request("tools/call", {"name": "nonexistent", "arguments": {}})

    print("\n【7】ping：保活/探活，返回空 result")
    await client.request("ping")

    print("\n【8】未知方法：协议层错误——响应里是 error 字段而非 result（错误码因实现而异，标准为 -32601）")
    await client.request("no/such_method")

    proc.terminate()
    await proc.wait()


if __name__ == "__main__":
    asyncio.run(main())
