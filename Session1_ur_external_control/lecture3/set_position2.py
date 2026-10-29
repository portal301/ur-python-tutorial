import asyncio
import socket

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

server_ip = "192.168.0.77"
robot_ip = "192.168.1.104"
script_path = "scripts/socket_set_position2.script"

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8').rstrip()  # Remove trailing newline

            print(f"Received from {addr}: {message}")

            if message == "req_data":
                print("Received data request")
                p_goal = [0.2626, -0.1777, 0.3691, 2.1936, 2.2199, -0.0141]
                p_rel = [0.0, 0.0, 0.10, 0.0, 0.0, 0.0]     # 목표에서 10cm 위 (베이스 기준)
                q_ref = [0.1232, -1.516, -1.6844, -1.4973, 1.5504, 3.2482]
                arr = p_goal + p_rel + q_ref # 18 floats
                float_string = "({})".format(','.join(map(str, arr)))
                writer.write(float_string.encode())

                await writer.drain()

            # writer.write(data)  # Echo back the received message
            # await writer.drain()
    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()

async def main(host='127.0.0.1', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")
    print("Sending script to the robot...")

    await asyncio.sleep(0.1)
    sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

    async with server:
        await server.serve_forever()

def getScriptFromPath(script_path):
    with open(script_path, 'r') as file:
        script = file.read()
    return script

def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.send((script + "\n").encode())
    socketClient.close()

def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, port)

if __name__ == "__main__":
    try:
        asyncio.run(main(host=server_ip))
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
