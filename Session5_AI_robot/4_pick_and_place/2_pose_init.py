import asyncio
import socket
import struct
from math import pi
import pyrealsense2 as rs
import numpy as np
import cv2

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

#TODO: 로봇 및 컴퓨터 ip 설정
server_ip = "192.168.0.87"
robot_ip = "192.168.0.31"
script_path = "scripts/pose_init.script"

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

            if message == "initialize":
                print("Received initialization request")
                #TODO: 로봇의 초기 위치(관절값) 조정
                p_init = [-90.000/180*pi, -100.000/180*pi, 70.000/180*pi, -60.000/180*pi, -90.000/180*pi, 0.000] # 로봇의 초기 joint state
                # p_init = [90.000/180*pi, -90.000/180*pi, 90.000/180*pi, -90.000/180*pi, -90.000/180*pi, 0.000]
                float_string = "({})\n".format(','.join(map(str, p_init)))
                writer.write(float_string.encode())
                await writer.drain()

    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    # except Exception as e:
    #     print("Error:", e)
    finally:
        print(f"Connection with {addr} closed")
        writer.close()
        # await writer.wait_closed()

async def main(host='0.0.0.0', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")
    print("Sending script to the robot...")

    await asyncio.sleep(0.1)
    sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)
    #camera_task = asyncio.create_task(update_camera())

    async with server:
        await server.serve_forever()
        #await camera_task

def getScriptFromPath(script_path):
    with open(script_path, 'r', encoding='utf-8') as file:
        script = file.read()
    return script

def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.send((script + "\n").encode())
    socketClient.close()

def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    print(script)
    sendScript(robot_url, script, port)

if __name__ == "__main__":
    try:
        asyncio.run(main(host=server_ip))
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
