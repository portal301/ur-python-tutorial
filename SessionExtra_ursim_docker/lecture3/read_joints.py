import math
import socket
import struct
import time

robot_ip = "127.0.0.1"   # 가상 로봇. 실물은 로봇 IP로 바꾸기
realtime_port = 30003    # 로봇이 상태를 계속 보내주는 포트


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("연결이 끊겼습니다")
        data += chunk
    return data


def read_joints(ip, port=realtime_port):
    """현재 관절 각도 6개(라디안)를 읽어 돌려줍니다."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    size = struct.unpack(">i", recv_exact(sock, 4))[0]   # 패킷 전체 길이
    packet = recv_exact(sock, size - 4)
    sock.close()
    # 패킷 앞부분을 offset 0부터 보기 (주석을 풀고 실행)
    # names = ["Time", "q target", "qd target", "qdd target", "I target", "M target", "q actual"]
    # sizes = [1, 6, 6, 6, 6, 6, 6]
    # pos = 0
    # for name, n in zip(names, sizes):
    #     values = struct.unpack(f">{n}d", packet[pos:pos + 8 * n])
    #     print(f"[{pos:3}] {name:<10}: " + ", ".join(f"{v:.3f}" for v in values))
    #     pos += 8 * n

    # 길이(4) 뒤로 double 31개(시간 1 + 목표값 6x5)를 건너뛰면 실제 관절값
    offset = 8 * 31
    return list(struct.unpack(">6d", packet[offset:offset + 48]))


if __name__ == "__main__":
    try:
        while True:
            q = read_joints(robot_ip)
            print("관절(deg):", [round(math.degrees(x), 1) for x in q])
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n종료")
