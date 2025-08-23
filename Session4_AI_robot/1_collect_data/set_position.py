### 8.1 현재 pose를 기준으로 하여 이동할 상대 pose를 전송하는 파이썬
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

server_ip = "192.168.1.5"
robot_ip = "192.168.1.4"
script_path = "scripts/set_position.script"

async def handle_client(reader, writer):
    # 클라이언트 소켓 주소(IP, Port) 가져오기
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    
    try:
        while True:
            # 클라이언트로부터 최대 1024바이트 데이터 수신
            data = await reader.read(1024)
            if not data:  # 연결 종료 시 루프 탈출
                break

            # 수신 데이터를 UTF-8로 디코딩하고 개행 제거
            message = data.decode('utf-8').rstrip()
            print(f"Received from {addr}: {message}")

            # "req_data" 요청을 받았을 경우
            if message == "req_data":
                print("Received data request")
                
                # 전송할 Pose 데이터 (상대 좌표 예제)
                p_rel = [0.0, 0.1, 0.0, 0.0, 0.0, 0.0]  # x, y, z, rx, ry, rz
                
                # 리스트를 쉼표로 연결하여 문자열로 변환하고 괄호로 감싸기
                float_string = "({})\n".format(','.join(map(str, p_rel)))
                
                writer.write(float_string.encode()) # UTF-8 인코딩 후 클라이언트로 전송
                await writer.drain()  # 버퍼가 비워질 때까지 대기

    except asyncio.CancelledError:
        # asyncio에서 태스크가 취소될 경우 예외 처리
        pass
    except ConnectionResetError:
        # 클라이언트 연결이 비정상적으로 종료된 경우
        print(f"Connection with {addr} reset")
    finally:
        # 연결 종료 처리
        print(f"Connection with {addr} closed")
        writer.close()

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
