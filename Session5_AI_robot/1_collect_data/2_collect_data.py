import asyncio
import socket
import struct
from math import cos, sin, pi
import numpy as np
import pyrealsense2 as rs
import cv2
import os


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

server_ip = "192.168.0.87"
robot_ip = "192.168.0.31"
script_path = "scripts/collect_data.script"

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

def get_relative_pose(radius, index, num_points=6):
    theta = 2 * pi * index / num_points
    
    # dx, dy, dz 계산 
    dx = radius * cos(theta)
    dy = radius * sin(theta)
    dz = 0.0

    # rx, ry, rz 계산
    # 1. 벡터 정규화
    v = np.array([dx, dy, 0.5 - dz]) 
    norm = np.linalg.norm(v)
    vx, vy, vz = v / norm

    # 2. 기준 z축 벡터
    z_axis = np.array([0, 0, 1])
    target_dir = np.array([vx, vy, vz])

    # 3. 외적과 내적 계산
    axis = np.cross(z_axis, target_dir)
    dot_product = np.dot(z_axis, target_dir)

    # 4. 각도 계산 (acos의 인자가 -1~1 범위 넘어가지 않도록 clip)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))

    # 5. 회전 벡터 (axis * angle)
    if np.linalg.norm(axis) == 0:
        rx, ry, rz = 0.0, 0.0, 0.0
    else:
        axis = axis / np.linalg.norm(axis)
        rx, ry, rz = - axis * angle

    return [dx, dy, dz, rx, ry, rz]

def generate_circle_poses(radius, num_points=6):
    poses = []
    for i in range(num_points):
        poses.append(get_relative_pose(radius, i, num_points))
    poses.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # 마지막에 원점으로 돌아오기
    return poses

def capture_image(pipeline, filename="output.jpg"):

    save_dir = "img"
    os.makedirs(save_dir, exist_ok=True)  # ./img 폴더가 없으면 생성

    # Flush old frames (RealSense가 최신 프레임을 제공하도록 몇 장 버림)
    for _ in range(5):
        pipeline.wait_for_frames()
    
    # Capture the frame
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    if not color_frame:
        print("[ERROR] No color frame captured.")
        return False

    # Convert to numpy array
    color_image = np.asanyarray(color_frame.get_data())

    # Save the image
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, color_image)
    print(f"[INFO] Image saved to: {filename}")
    return True

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

                #TODO: 적절한 반지름 설정. m단위
                poses = generate_circle_poses(0.10) # 0.10m radius
                for pose in poses:
                    print2(f"Sending pose: {pose}", Color.GREEN)
                    float_string = "({})\n".format(','.join(map(str, pose)))
                    writer.write(float_string.encode())
                    await writer.drain()
                    await asyncio.sleep(0.1)  # 다음 포즈 보내기 전 대기
                    
                    # "reached"가 도착하면 이미지 캡쳐
                    data = await reader.read(1024)
                    message = data.decode('utf-8').rstrip()
                    if message == "reached":
                        capture_image(pipeline, f"pose_{poses.index(pose)}.jpg")
                    
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

async def main(host='0.0.0.0', port=12345):
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
