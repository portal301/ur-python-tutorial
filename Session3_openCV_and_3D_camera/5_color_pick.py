# 노란 물체를 찾아서 집고, 정해둔 곳에 놓기
# - 4_click_move와 같은 구조. 다른 점은 "클릭" 대신 "노란색 자동 찾기"로 점을 정함
# - 로봇이 홈(사진 찍는 자세)에 있을 때만 찾음:
#   스크립트를 보내면 busy = True → 로봇이 집고·놓고·홈으로 돌아온 뒤 "done"을 보내면 busy = False
# - 카메라 좌표 → 로봇 베이스 좌표 변환은 로봇 스크립트(scripts/color_pick.script)가 함
# - 로봇 스크립트는 시작할 때의 자세를 "홈"으로 기억하고 마지막에 그 자세로 돌아옴
#   → 처음에 로봇을 사진 찍을 자세(물체가 화면에 보이는 자세)에 두고 실행
# - q = 종료, r = busy 강제 해제 (로봇이 중간에 멈췄을 때)
# - 펜던트는 원격제어(Remote) 모드
import asyncio
import os
import socket
import numpy as np, cv2, pyrealsense2 as rs


# ============================================================
# 1. 설정값
# ============================================================
PORT_PRIMARY_CLIENT = 30001

robot_ip = "192.168.1.104"
script_path = os.path.join(os.path.dirname(__file__), "scripts", "color_pick.script")

TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전

# 노란색 범위 (B, G, R). 조명에 따라 다르니 "yellow mask" 창을 보면서 조정
YELLOW_LOWER = (0, 70, 100)
YELLOW_UPPER = (90, 210, 255)
MIN_PIXELS = 500        # 노란 덩어리가 이보다 작으면 "없음"으로 판단 (작은 잡음 무시)
IGNORE_X = 540          # 이 x보다 오른쪽은 무시 (화면 오른쪽에 보이는 노란 그리퍼 부품)

p_cam = None            # 찾은 점 (카메라 기준, m). 아직 없으면 None
busy = False            # True면 로봇이 일하는 중 → 찾지도 보내지도 않음


# ============================================================
# 2. 로봇 통신 (4_click_move와 같은 구조 + "done" 받기)
# ============================================================
async def handle_client(reader, writer):
    global busy
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8').rstrip()  # Remove trailing newline

            print(f"Received from {addr}: {message}")

            if message == "req_data" and p_cam is not None:
                print("Received data request")
                p_goal = list(p_cam) + [0.0, 0.0, 0.0]      # 카메라로 찾은 점
                arr = p_goal + TCP_CAMERA                   # 12 floats
                float_string = "({})".format(','.join(map(str, arr)))
                writer.write(float_string.encode())
                await writer.drain()

            if message == "done":                           # 로봇이 홈으로 돌아옴 → 다시 찾기 시작
                busy = False
                print("로봇 작업 끝. 다시 노란 물체를 찾습니다.")
    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()


def getScriptFromPath(script_path):
    # newline='' : 주석 안의 \r 을 줄바꿈으로 바꾸지 않도록 원본 그대로 읽음 (Day2 gripper.py와 같음)
    with open(script_path, 'r', encoding='utf-8', newline='') as file:
        script = file.read()
    return script.replace('\r', '')


async def sendScriptFile(robot_url, script_path, port=PORT_PRIMARY_CLIENT):
    script = getScriptFromPath(script_path)
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((robot_url, port))
    socketClient.sendall((script + "\n").encode())
    # 그리퍼 스크립트가 길어서 바로 닫으면 뒷부분이 잘림 → 잠깐 기다린 뒤 닫음 (Day2 gripper.py와 같음)
    # time.sleep 대신 asyncio.sleep: 기다리는 동안에도 서버(handle_client)가 req_data에 답할 수 있게
    await asyncio.sleep(3)
    socketClient.close()


# ============================================================
# 3. 카메라 (4_click_move와 같음)
# ============================================================
def start_camera():
    """RealSense 컬러 + 깊이 시작. (pipe, align) 반환"""
    pipe = rs.pipeline(); cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipe.start(cfg)
    align = rs.align(rs.stream.color)                # 깊이를 컬러 화면에 맞춰 정렬
    return pipe, align


def get_frame(pipe, align):
    """프레임 한 장 받기. (컬러 이미지, 깊이 프레임, 내부 파라미터) 반환"""
    f = align.process(pipe.wait_for_frames())
    color = np.asanyarray(f.get_color_frame().get_data())
    depth = f.get_depth_frame()
    intr = f.get_color_frame().profile.as_video_stream_profile().intrinsics
    return color, depth, intr


def pixel_to_camera(u, v, depth, intr):
    """픽셀 (u, v) → 카메라 기준 3D 점(m). 깊이를 못 읽으면 None"""
    z = depth.get_distance(u, v)                                        # 픽셀 (u, v)까지의 거리(m)
    if z <= 0:                                                          # 0이면 깊이를 못 읽은 것
        return None
    return np.array(rs.rs2_deproject_pixel_to_point(intr, [u, v], z))   # 픽셀(u, v) + 깊이(z) → 3D 점


# ============================================================
# 4. 노란색 찾기 (2_similar_color의 "범위 안에 드는 픽셀 고르기"와 같은 생각)
# ============================================================
def find_yellow(color):
    """노란 픽셀들의 중심 (u, v)와 마스크 반환. 없으면 (None, 마스크)"""
    # 2_similar_color에서는 이중 for문으로 직접 비교했지만, 카메라 화면은 매 프레임 바뀌어서 너무 느림
    # → 같은 일을 한 번에 해주는 cv2.inRange 사용 (범위 안 = 255, 밖 = 0)
    mask = cv2.inRange(color, YELLOW_LOWER, YELLOW_UPPER)
    mask[:, IGNORE_X:] = 0                          # 오른쪽 영역 지우기
    # 물체가 여러 개면 전체 평균은 물체 사이 빈 곳이 됨 → 붙어 있는 덩어리별로 나눠서 가장 큰 것 하나만
    n, labels, stats, centers = cv2.connectedComponentsWithStats(mask)
    if n < 2:                                       # 0번은 배경. 덩어리가 없음
        return None, mask
    best = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])   # 가장 큰 덩어리 번호
    if stats[best, cv2.CC_STAT_AREA] < MIN_PIXELS:
        return None, mask
    cx, cy = centers[best]
    return (int(cx), int(cy)), mask                 # 그 덩어리의 중심점


# ============================================================
# 5. 카메라 창 (노란색 찾기 → 보이면 로봇에 스크립트 보내기)
# ============================================================
async def camera_loop():
    global p_cam, busy
    pipe, align = start_camera()

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)
            center, mask = find_yellow(color)

            # (1) 로봇이 홈에서 쉬는 중이고 노란 물체가 보이면 → 점 계산해서 보내기
            if not busy and center is not None:
                point = pixel_to_camera(center[0], center[1], depth, intr)
                if point is None:
                    print("깊이를 못 읽었습니다. 다시 찾습니다.")
                else:
                    p_cam = point
                    print(f"노란 물체 {center} → 카메라 기준 점 {np.round(p_cam*1000,1)} mm. 로봇에 보냅니다.")
                    busy = True                     # 보내기 전에 먼저 True (로봇 일하는 동안 또 보내지 않게)
                    await sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

            # (2) 화면 표시
            if center is not None:
                cv2.drawMarker(color, center, (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
            state = "BUSY" if busy else "READY"
            cv2.putText(color, state, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("color pick", color)
            cv2.imshow("yellow mask", mask)

            # (3) 키 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                busy = False; print("busy 강제 해제")

            await asyncio.sleep(0)                  # 서버(handle_client)에 차례 넘기기
    finally:
        pipe.stop(); cv2.destroyAllWindows()


# ============================================================
# 6. 메인
# ============================================================
async def main(host='0.0.0.0', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    await camera_loop()                             # 카메라 창이 열려 있는 동안 서버도 열려 있음
    server.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
