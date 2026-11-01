# 클릭한 점 위로 로봇 보내기 (카메라-툴 캘리브레이션 확인용)
# - 화면에서 점을 클릭 → m을 누르면 그리퍼 끝(TCP)이 그 점의 30cm 위 → 2cm 위까지 내려감 → 다시 30cm 위로 올라옴
# - Day1 set_position2와 같은 구조: PC가 서버를 열고, 로봇 스크립트가 접속해 "req_data"를 보내면
#   handle_client가 좌표를 답해줌. 이번에는 직접 적은 숫자 대신 "카메라로 찾은 좌표"를 보냄
# - 카메라 좌표 → 로봇 베이스 좌표 변환은 로봇 스크립트(scripts/click_move.script)가 함
# - m = 이동, c = 취소, q = 종료
# - 자세(회전)는 지금 그대로 두고 위치만 바꿈. 펜던트는 원격제어(Remote) 모드
import asyncio
import os
import socket
import numpy as np, cv2, pyrealsense2 as rs


# ============================================================
# 1. 설정값
# ============================================================
PORT_PRIMARY_CLIENT = 30001

robot_ip = "192.168.1.104"
script_path = os.path.join(os.path.dirname(__file__), "scripts", "click_move.script")

TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전
HOVER = 0.30                                     # 점 위 높이(m)

p_cam = None        # 클릭한 점 (카메라 기준, m). 아직 없으면 None


# ============================================================
# 2. 로봇 통신 (Day1 set_position2와 같은 구조)
# ============================================================
async def handle_client(reader, writer):
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
                p_goal = list(p_cam) + [0.0, 0.0, 0.0]      # Day1에서 직접 적었던 p_goal 자리에 카메라로 찾은 점
                p_rel = [0.0, 0.0, HOVER, 0.0, 0.0, 0.0]    # 점에서 HOVER만큼 위 (베이스 기준)
                arr = p_goal + TCP_CAMERA + p_rel           # 18 floats
                float_string = "({})".format(','.join(map(str, arr)))
                writer.write(float_string.encode())
                await writer.drain()
    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()


def getScriptFromPath(script_path):
    with open(script_path, 'r', encoding='utf-8') as file:
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


# ============================================================
# 3. 카메라
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
# 4. 카메라 창 (클릭 → 점 저장, m → 로봇에 스크립트 보내기)
# ============================================================
clicked = []        # 마우스로 클릭한 픽셀 (u, v)가 여기 들어옴


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked.append((x, y))


async def camera_loop():
    global p_cam
    pipe, align = start_camera()
    cv2.namedWindow("click to move")
    cv2.setMouseCallback("click to move", on_mouse)
    marker = None                                   # 화면에 + 표시할 픽셀 (u, v)

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)

            # (1) 클릭했으면 카메라 기준 3D 점 계산
            if clicked:
                u, v = clicked.pop()
                point = pixel_to_camera(u, v, depth, intr)
                if point is None:
                    print("깊이를 못 읽었습니다. 다른 점을 클릭하세요.")
                else:
                    p_cam, marker = point, (u, v)
                    print(f"클릭 ({u},{v}) → 카메라 기준 점 {np.round(p_cam*1000,1)} mm.  m=이동 / c=취소")

            # (2) 화면 표시 (점이 있으면 클릭한 곳에 + 표시)
            if p_cam is not None:
                cv2.drawMarker(color, marker, (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
            cv2.imshow("click to move", color)

            # (3) 키 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                p_cam = None; print("취소")
            if key == ord("m") and p_cam is not None:
                print("Sending script to the robot...")
                sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

            await asyncio.sleep(0)                  # 서버(handle_client)에 차례 넘기기
    finally:
        pipe.stop(); cv2.destroyAllWindows()


# ============================================================
# 5. 메인
# ============================================================
async def main(host='0.0.0.0', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    await camera_loop()                             # Day1의 serve_forever() 대신: 카메라 창이 열려 있는 동안 서버도 열려 있음
    server.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
