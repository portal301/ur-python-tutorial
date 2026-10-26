# Primary interface
import socket

PORT_PRIMARY_CLIENT = 30001
PORT_SECONDARY_CLIENT = 30002

## Phase2: elaborate the functions
def getScriptFromPath(script_path):
    # Open the file in read mode
    with open(script_path, 'r', encoding='utf-8') as file:
    # with open(script_path, 'r') as file:
        # Read the contents of the file
        script = file.read()
        # print(script)
    return script

def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.settimeout(5)
    socketClient.sendall((script + "\n").encode())
    # 스크립트가 길어서, 바로 닫으면 뒷부분이 잘림 → "다 보냈다"고 알리고 로봇이 닫을 때까지 기다림
    socketClient.shutdown(socket.SHUT_WR)
    while socketClient.recv(4096):   # 로봇이 보내는 상태 데이터는 읽어서 버림
        pass
    socketClient.close()

def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, port)

if __name__ == "__main__":
    robot_url = "192.168.0.31"
    # script_path = "scripts/example_urcaps_schunk.script"
    # script_path = "scripts/example_urcaps_onrobot.script"
    script_path = "scripts/urcaps_copy5.script"
    sendScriptFile(robot_url, script_path, PORT_PRIMARY_CLIENT)


