# 그리퍼 스크립트를 로봇으로 보내기
# 실행: Session2_gripper_urcaps 폴더에서 python lecture2/gripper.py
import socket
import time

PORT_PRIMARY_CLIENT = 30001

robot_url = "192.168.1.104"
script_path = "practice/gripper_open_close.script"     # 실습 1: 그리퍼 열고 닫기
# script_path = "practice/pick_and_place.script"       # 실습 2: 저장한 위치로 Pick and Place
# 정답 확인: "practice/" 대신 "answer/"


def getScriptFromPath(script_path):
    # newline='' : 주석 안의 \r 을 줄바꿈으로 바꾸지 않도록 원본 그대로 읽음
    with open(script_path, 'r', encoding='utf-8', newline='') as file:
        script = file.read()
    # PolyScope가 만든 스크립트에는 주석 중간에 \r 이 섞여 있을 수 있음 → 제거
    return script.replace('\r', '')


def sendScript(robot_url, script, port=PORT_PRIMARY_CLIENT):
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.sendall((script + "\n").encode())
    # 스크립트가 길어서, 바로 닫으면 뒷부분이 잘림 → 전송이 끝날 때까지 잠깐 기다린 뒤 닫음
    time.sleep(3)
    socketClient.close()


if __name__ == "__main__":
    script = getScriptFromPath(script_path)
    sendScript(robot_url, script, PORT_PRIMARY_CLIENT)
    print("스크립트 전송 완료:", script_path)
