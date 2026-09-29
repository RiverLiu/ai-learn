import asyncio
import websockets

async def handler(websocket):

    async for message in websocket:
        print("收到:", message)

        await websocket.send(
            f"服务器收到: {message}"
        )

# Dispatch er

async def main():
    server = await websockets.serve(
        handler,
        "0.0.0.0",
        8765
    )

    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())