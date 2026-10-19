# make a socket client connecting to "172.20.2.131:12345"
import asyncio

async def main():
    reader, writer = await asyncio.open_connection("172.20.2.139", 12345)

    # send initialization message
    writer.write(b"initialize\n")
    await writer.drain()

    try:
        data = await reader.read(1024)
        print(f"Received: {data.decode()}")
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
