# Primary interface
import socket
import time

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

## Phase2: elaborate the functions
def getScriptFromPath(script_path):
    # Open the file in read mode
    # newline='' : 주석 안의 \r 을 줄바꿈으로 바꾸지 않도록 원본 그대로 읽음
    with open(script_path, 'r', encoding='utf-8', newline='') as file:
    # with open(script_path, 'r') as file:
        # Read the contents of the file
        script = file.read()
        # print(script)
    # PolyScope가 만든 스크립트에는 주석 중간에 \r 이 섞여 있을 수 있음 → 제거
    return script.replace('\r', '')

def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.sendall((script + "\n").encode())
    # 스크립트가 길어서, 바로 닫으면 뒷부분이 잘림 → 전송이 끝날 때까지 잠깐 기다린 뒤 닫음
    time.sleep(3)
    socketClient.close()

def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, port)

if __name__ == "__main__":
    robot_url = "192.168.1.104"
    # script_path = "scripts/example_urcaps_schunk.script"
    # script_path = "scripts/example_urcaps_onrobot.script"
    script_path = "scripts/example_urcaps_onrobot_rg2ft.script"
    # script_path = "scripts/gripper_open_close.script"   # 실습: 그리퍼 열고 닫기 (완성본)
    sendScriptFile(robot_url, script_path, PORT_PRIMARY_CLIENT)


