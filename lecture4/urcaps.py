import asyncio
import socket
import struct

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print2(str, color=Color.YELLOW):
    print(color, str, Color.END)

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

server_ip = "192.168.0.7"
robot_ip = "192.168.0.21"
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

            if message == "current_pos":
                print("Received position data request")
                p_ = await handle_pos_data(reader)
                print2(f"p_: {p_}", Color.GREEN)
                q_ = await handle_pos_data(reader)
                print2(f"q_: {q_}", Color.GREEN)
            elif message == "req_data":
                print("Received data request")
                p_goal = [-0.6645,-0.20302,-0.02930,2.627,1.851,-0.103]
                p_rel = [0.0, 0.0, -0.03, 0.0, 0.0, 0.0]
                q_ref = [0.0183, -1.4455, 2.2758, -2.4493, 4.9255, 0.3495]
                peripheral = [0,0,0]
                arr = p_goal + p_rel + q_ref + peripheral # 21 floats
                float_string = "({})\n".format(','.join(map(str, arr)))
                writer.write(float_string.encode())

                await writer.drain()

    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()

async def handle_pos_data(reader):
    integers_data = []
    # Receive 24 bytes (6 integers = 6 * 4 bytes = 24 bytes) 
    data = await reader.readexactly(24)
    # Unpack the 6 short integers from the received data
    print("position data:", data)
    integers_data = struct.unpack('>iiiiii', data)
    actual_pos_data = [x/10000 for x in integers_data]

    return actual_pos_data

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