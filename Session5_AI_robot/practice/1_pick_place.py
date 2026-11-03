# 1단계: AI(YOLO)가 찾은 물체를 집어서 놓을 곳(PLACE)에 내려놓기
# - Day4 4단계(물체 위로 이동)에 "내려가서 잡기 → 놓을 곳에 놓기"를 더함. 각도는 아직 신경 쓰지 않음
# - TODO 1은 로봇 스크립트(scripts/pick_place.script) 안에 있음
# - 순서: 물체 위 → 내려감 → 잡기 → 올라옴 → 놓을 곳 위 → 내려감 → 놓기 → 올라옴
# - 모델은 OBB 모델이지만 여기서는 박스 중심만 씀 (각도는 2단계부터)
# - t = 물체 찾기, m = 실행, c = 취소, q = 종료
# - t를 누른 뒤 m을 누를 때까지 로봇을 움직이지 말 것 (로봇이 '지금 자세' 기준으로 계산함)
# - 로봇이 움직이는 동안에는 m을 다시 누르지 않기 (새 스크립트가 지금 동작을 끊고 그 자리에서 다시 시작함)
# - 펜던트는 원격제어(Remote) 모드
import asyncio
import os
import socket
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
PORT_PRIMARY_CLIENT = 30001

robot_ip = "192.168.1.104"
script_path = os.path.join(os.path.dirname(__file__), "scripts", "pick_place.script")

TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전 (Day3와 같음)
MODEL_PATH = ""
TARGET = ""
CONF_MIN = 0.5

plan = None         # (u, v, 카메라 기준 점). 아직 없으면 None


# ============================================================
# 2. 로봇 통신
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

            if message == "req_data" and plan is not None:
                print("Received data request")
                p_goal = list(plan[2]) + [0.0, 0.0, 0.0]    # 카메라로 찾은 물체 중심
                arr = p_goal + TCP_CAMERA                   # 12 floats
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
# 3. 카메라 (Day4와 같음)
# ============================================================
def start_camera():
    """RealSense 컬러 + 깊이 시작. (pipe, align) 반환"""
    pipe = rs.pipeline(); cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipe.start(cfg)
    align = rs.align(rs.stream.color)
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
    z = depth.get_distance(u, v)
    if z <= 0:
        return None
    return np.array(rs.rs2_deproject_pixel_to_point(intr, [u, v], z))


# ============================================================
# 4. 물체 고르기 (Day4 2단계와 같음, boxes → obb만 다름)
# ============================================================
def pick_target(result, names):
    """탐지 결과에서 TARGET 중 가장 확실한 박스 하나 고르기. 없으면 None"""
    best, best_conf = None, 0
    for box in result.obb:
        name = names[int(box.cls[0])]
        conf = float(box.conf[0])
        if name != TARGET or conf < CONF_MIN:
            continue
        if conf > best_conf:
            best, best_conf = box, conf
    return best



# ============================================================
# 5. 카메라 창 (YOLO 탐지 → t로 목표 정하기, m → 로봇에 스크립트 보내기)
# ============================================================
async def camera_loop():
    global plan
    model = YOLO(MODEL_PATH)
    pipe, align = start_camera()

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)

            result = model(color, verbose=False)[0]
            box = pick_target(result, model.names)
            if box is not None:
                corners = np.array(box.xyxyxyxy[0].tolist(), dtype=np.int32)
                cv2.polylines(color, [corners], True, (0, 255, 0), 2)

            if plan:
                cv2.drawMarker(color, plan[:2], (0, 255, 255), cv2.MARKER_TILTED_CROSS, 24, 2)
            cv2.imshow("pick place", color)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                plan = None; print("취소")
            if key == ord("t"):
                if box is None:
                    print(f"{TARGET}을(를) 찾지 못했습니다.")
                else:
                    # TODO 2: 박스 중심 픽셀 u, v 구하기 (xywhr = 중심 x, y, 폭, 높이, 각도. 픽셀은 정수)
                    x, y, w, h, r = box.xywhr[0].tolist()
                    u, v = ____
                    p_cam = pixel_to_camera(u, v, depth, intr)
                    if p_cam is None:
                        print("깊이를 못 읽었습니다. 물체 위치를 바꿔 보세요.")
                    else:
                        plan = (u, v, p_cam)
                        print(f"{TARGET} 중심 ({u},{v})")
                        print(f"   카메라 기준 점 {np.round(p_cam*1000,1)} mm.  m=실행 / c=취소")
            if key == ord("m") and plan:
                print("Sending script to the robot...")
                await sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

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
