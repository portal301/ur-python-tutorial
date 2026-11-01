# 4단계: AI(YOLO)가 고른 물체 위로 로봇 보내기
# - Day3 click_move에서 "마우스 클릭" 자리에 2·3단계를 넣음. 로봇 통신 구조는 Day3와 같음
#   (PC가 서버를 열고, 로봇 스크립트가 접속해 "req_data"를 보내면 handle_client가 좌표를 답해줌)
# - 카메라 좌표 → 로봇 베이스 좌표 변환은 로봇 스크립트(scripts/yolo_move.script)가 함
# - t = 목표 정하기, m = 이동, c = 취소, q = 종료
# - 자세(회전)는 지금 그대로 두고 위치만 바꿈. 펜던트는 원격제어(Remote) 모드
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
script_path = os.path.join(os.path.dirname(__file__), "scripts", "yolo_move.script")

TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전
HOVER = 0.30                                     # 물체 위 높이(m)
MODEL_PATH = "yolo11n.pt"                        # COCO 사전학습 모델
TARGET = "cup"                                   # 찾을 물체 이름 (COCO 클래스 이름)
CONF_MIN = 0.5                                   # 이보다 신뢰도가 낮으면 무시

p_cam = None        # 고른 물체 중심 (카메라 기준, m). 아직 없으면 None


# ============================================================
# 2. 로봇 통신 (Day3와 같음)
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
                p_goal = list(p_cam) + [0.0, 0.0, 0.0]      # 카메라로 찾은 물체 중심
                p_rel = [0.0, 0.0, HOVER, 0.0, 0.0, 0.0]    # 물체에서 HOVER만큼 위 (베이스 기준)
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
# 3. 카메라 (Day3와 같음)
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
    z = depth.get_distance(u, v)
    if z <= 0:
        return None
    return np.array(rs.rs2_deproject_pixel_to_point(intr, [u, v], z))


# ============================================================
# 4. 물체 고르기·그리기 (2·3단계와 같음)
# ============================================================
def pick_target(result, names):
    """탐지 결과에서 로봇이 갈 박스 하나 고르기. 없으면 None"""
    best, best_conf = None, 0
    for box in result.boxes:
        name = names[int(box.cls[0])]
        conf = float(box.conf[0])
        if name != TARGET:
            continue
        if conf < CONF_MIN:
            continue
        if conf > best_conf:
            best, best_conf = box, conf
    return best


def draw_target(img, box, names):
    """고른 박스, 이름·신뢰도, 중심을 img 위에 그리기"""
    x, y, w, h = box.xywh[0].tolist()
    x1, y1 = int(x - w / 2), int(y - h / 2)
    x2, y2 = int(x + w / 2), int(y + h / 2)
    label = f"{names[int(box.cls[0])]} {float(box.conf[0]):.2f}"
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.drawMarker(img, (int(x), int(y)), (0, 0, 255), cv2.MARKER_CROSS, 24, 2)


# ============================================================
# 5. 카메라 창 (YOLO 탐지 → t로 목표 정하기, m → 로봇에 스크립트 보내기)
# ============================================================
async def camera_loop():
    global p_cam
    model = YOLO(MODEL_PATH)
    pipe, align = start_camera()
    marker = None                                   # 화면에 노란 + 표시할 픽셀 (u, v)

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)

            # (1) YOLO로 탐지하고 물체 하나 고르기 (Day3의 마우스 클릭 자리)
            result = model(color, verbose=False)[0]
            box = pick_target(result, model.names)
            if box is not None:
                draw_target(color, box, model.names)

            # (2) 화면 표시 (목표가 있으면 그 자리에 노란 + 표시)
            if p_cam is not None:
                cv2.drawMarker(color, marker, (0, 255, 255), cv2.MARKER_TILTED_CROSS, 24, 2)
            cv2.imshow("yolo move", color)

            # (3) 키 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                p_cam = None; print("취소")
            if key == ord("t"):
                if box is None:
                    print(f"{TARGET}을(를) 찾지 못했습니다.")
                else:
                    x, y, w, h = box.xywh[0]
                    u, v = int(x), int(y)                        # 고른 물체의 중심 = Day3의 클릭한 점
                    point = pixel_to_camera(u, v, depth, intr)
                    if point is None:
                        print("깊이를 못 읽었습니다. 물체 위치를 바꿔 보세요.")
                    else:
                        p_cam, marker = point, (u, v)
                        print(f"{TARGET} 중심 ({u},{v}) → 카메라 기준 점 {np.round(p_cam*1000,1)} mm.  m=이동 / c=취소")
            if key == ord("m") and p_cam is not None:
                print("Sending script to the robot...")
                sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

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
