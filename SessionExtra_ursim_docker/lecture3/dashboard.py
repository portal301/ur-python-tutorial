import socket

robot_ip = "127.0.0.1"   # 가상 로봇. 실물은 로봇 IP로 바꾸기
dashboard_port = 29999   # 대시보드 서버

commands = ["robotmode", "safetystatus", "programState", "get robot model"]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((robot_ip, dashboard_port))
print(sock.recv(1024).decode().strip())   # 접속 인사말

for cmd in commands:
    sock.send((cmd + "\n").encode())     # 명령은 줄바꿈으로 끝냄
    reply = sock.recv(1024).decode().strip()
    print(f"{cmd:<16} -> {reply}")

sock.close()
