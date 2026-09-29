import asyncio
import websockets

async def client():

    async with websockets.connect(
        "ws://localhost:8765"
    ) as ws:

        await ws.send("Hello")

        result = await ws.recv()

        print(result)

if __name__ == '__main__':
    asyncio.run(client())