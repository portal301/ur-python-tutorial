# 그리퍼 스크립트를 로봇으로 보내기
# 실행: Session2_gripper_urcaps 폴더에서 python lecture2/gripper.py
import socket

PORT_PRIMARY_CLIENT = 30001

robot_url = "192.168.0.110"
script_path = "practice/gripper_open_close.script"     # 실습 1: 그리퍼 열고 닫기
# script_path = "practice/pick_and_place.script"       # 실습 2: 하드코딩 좌표로 집고 놓기
# 정답 확인: "practice/" 대신 "answer/"


def getScriptFromPath(script_path):
    with open(script_path, 'r', encoding='utf-8') as file:
        script = file.read()
    return script


def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.send((script + "\n").encode())
    socketClient.close()


if __name__ == "__main__":
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, PORT_PRIMARY_CLIENT)
    print("스크립트 전송 완료:", script_path)
