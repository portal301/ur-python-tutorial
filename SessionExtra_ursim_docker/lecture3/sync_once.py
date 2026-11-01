import socket

from read_joints import read_joints

# 따라 할 로봇 (가상 로봇 1)
source_ip = "127.0.0.1"
source_realtime_port = 30003

# 따라 움직일 로봇 (기본: 포트를 바꿔 띄운 가상 로봇 2)
# 실물로 시연할 때: target_ip = 로봇 IP, target_script_port = 30002
target_ip = "127.0.0.1"
target_script_port = 40002

ACC = 0.5             # 관절 가속도 (rad/s^2)
VEL = 0.2             # 관절 속도 (rad/s)


def send_script(ip, port, script):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send((script + "\n").encode())
    sock.close()


def sync_once():
    q = read_joints(source_ip, source_realtime_port)
    q_text = ", ".join(f"{x:.5f}" for x in q)
    script = f"movej([{q_text}], a={ACC}, v={VEL})"
    print("보냄:", script)
    send_script(target_ip, target_script_port, script)


if __name__ == "__main__":
    print("가상 로봇을 움직인 뒤 Enter를 누르면 대상 로봇이 따라갑니다. (종료: q)")
    try:
        while True:
            if input("> ").strip().lower() == "q":
                break
            sync_once()
    except (KeyboardInterrupt, EOFError):
        pass
    print("종료")
