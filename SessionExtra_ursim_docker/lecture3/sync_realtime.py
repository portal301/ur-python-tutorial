import socket

from read_joints import read_joints
from sync_once import send_script

# 따라 할 로봇 (가상 로봇 1)
source_ip = "127.0.0.1"
source_realtime_port = 30003

# 따라 움직일 로봇 (기본: 가상 로봇 2)
# 실물 시연(강사만): target_ip = 로봇 IP, target_script_port = 30002
target_ip = "127.0.0.1"
target_script_port = 40002

# 로봇이 접속해 올 PC 서버. 로봇 쪽 IP는 scripts/sync_realtime.script 의 server_ip
server_ip = "0.0.0.0"
server_port = 12345
script_path = "scripts/sync_realtime.script"


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_ip, server_port))
    server.listen(1)
    print(f"서버 대기 중: {server_ip}:{server_port}")

    with open(script_path, "r") as f:
        send_script(target_ip, target_script_port, f.read())

    conn, addr = server.accept()
    print(f"로봇 접속: {addr}. 가상 로봇 1을 움직여 보세요. (종료: Ctrl+C)")

    try:
        buf = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buf += data
            # 로봇이 "next" 를 보낼 때마다 지금 관절값을 하나 보냄
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if line.strip() == b"next":
                    q = read_joints(source_ip, source_realtime_port)
                    msg = "(" + ",".join(f"{x:.5f}" for x in q) + ")\n"
                    conn.send(msg.encode())
    except KeyboardInterrupt:
        pass
    finally:
        # 연결을 끊으면 로봇은 1초 안에 스스로 멈춤
        conn.close()
        server.close()
        print("종료")
