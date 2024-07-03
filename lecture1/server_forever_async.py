import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")
            writer.write(data)  # Echo back the received message
            await writer.drain()
    except asyncio.CancelledError:
        pass
    finally:
        print(f"Connection with {addr} closed")
        writer.close()
        await writer.wait_closed()

async def main(host='127.0.0.1', port=65432):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
