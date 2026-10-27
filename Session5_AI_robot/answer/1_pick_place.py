# 1단계: AI(YOLO)가 찾은 물체를 집어서 놓을 곳(PLACE)에 내려놓기
# - Day4 4단계(물체 위로 이동)에 "내려가서 잡기 → 놓을 곳에 놓기"를 더함. 각도는 아직 신경 쓰지 않음
# - 원래 과정(Session4 4_pickup_obb)과 같은 틀:
#   PC = 물체 찾기 + 서버,  로봇 = PC에 물어보고(req_data) 좌표 계산 + 움직임 (scripts/pick_place.script)
# - 순서: 물체 위 → 내려감 → 잡기 → 올라옴 → 놓을 곳 위 → 내려감 → 놓기 → 올라옴
# - 모델은 OBB 모델이지만 여기서는 박스 중심만 씀 (각도는 2단계부터)
# - t = 물체 찾기, m = 실행, c = 취소, 스페이스 = 정지 명령, q = 종료
# - t를 누른 뒤 m을 누를 때까지 로봇을 움직이지 말 것 (로봇이 '지금 자세' 기준으로 계산함)
# - 실행: Session5_AI_robot 폴더에서 python answer/1_pick_place.py
import socket
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
ROBOT_IP = "192.168.0.3"
PC_IP = "192.168.0.2"                            # 로봇이 접속할 PC의 이더넷 IP (Day1 lecture3와 같음)
PORT = 12345                                     # PC 서버 포트
TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전 (Day3와 같음, 플랜지 기준 z 0.019 - 0.2387)
HOVER = 0.30                                     # 물체 위 높이(m)
TOOL_DOWN = [0.0611, 3.141, 0.0]                 # 툴이 정확히 아래(베이스 -z)를 보는 회전 rx, ry, rz. 집고 놓을 때 이 회전을 씀. 강의장에서 다시 재기
GRASP_OFFSET = [0.0, 0.0, 0.05]                  # 물체 윗면 기준 잡는 위치 보정 x, y, z(m, 베이스 기준으로 더함). z가 음수면 더 내려감. 강의장에서 그리퍼에 맞춰 조정
SPEED_V, SPEED_A = 0.05, 0.2                     # 직선 이동 속도(m/s), 가속도
PLACE = [0.40, -0.20]                            # TODO 직접 재기!! 놓을 곳의 베이스 기준 x, y(m) (티치펜던트로 그 자리 위에 TCP를 두고 읽은 값)
GRIP_OPEN, GRIP_CLOSE, GRIP_FORCE = 100.0, 20.0, 40.0   # 그리퍼 열기·닫기 폭(mm), 힘(N). 강의장에서 물체에 맞춰 조정
MODEL_PATH = ""
TARGET = ""
CONF_MIN = 0.5
GRIPPER_SCRIPT = "../Session2_gripper_urcaps/answer/gripper_open_close.script"   # Day2 그리퍼 스크립트 (위쪽 OnRobot 정의만 가져다 씀)
ROBOT_SCRIPT = "answer/scripts/pick_place.script"                         # 로봇이 할 일


# ============================================================
# 2. 로봇에 프로그램 보내기
# ============================================================
def send(script):
    """URScript 프로그램을 30002 포트로 보내기"""
    r = socket.create_connection((ROBOT_IP, 30002), timeout=3)
    r.sendall((script + "\n").encode())
    # 스크립트가 길어서, 바로 닫으면 뒷부분이 잘림 → "다 보냈다"고 알리고 로봇이 닫을 때까지 기다림
    r.shutdown(socket.SHUT_WR)
    try:
        while r.recv(4096):          # 로봇이 보내는 상태 데이터는 읽어서 버림
            pass
    except socket.timeout:
        pass
    r.close()


def stop():
    """정지 명령 보내기"""
    send("def stop_now():\n  stopl(0.5)\nend")
    print(">> 정지 명령 보냄")


def read_file(path):
    with open(path, encoding="utf-8") as file:
        return file.read()


def gripper_header():
    """Day2 그리퍼 스크립트에서 OnRobot 정의 부분(본문 앞까지)만 읽어 오기"""
    mark = "  # end: URCap Installation Node\n"
    return read_file(GRIPPER_SCRIPT).rsplit(mark, 1)[0] + mark   # 마지막 경계 줄까지 (앞쪽 다른 URCap에도 같은 줄이 있음)


def settings_lines():
    """1번 설정값을 URScript 변수로 바꾼 줄들 (로봇 프로그램이 이 이름을 씀)"""
    return "\n".join([
        f'  PC_IP = "{PC_IP}"',
        f"  PORT = {PORT}",
        "  TCP_CAMERA = p[%s]" % ", ".join(str(x) for x in TCP_CAMERA),
        f"  HOVER = {HOVER}",
        f"  TOOL_DOWN = {TOOL_DOWN}",
        f"  GRASP_OFFSET = {GRASP_OFFSET}",
        f"  PLACE = {PLACE}",
        f"  SPEED_V = {SPEED_V}",
        f"  SPEED_A = {SPEED_A}",
        f"  GRIP_OPEN = {GRIP_OPEN}",
        f"  GRIP_CLOSE = {GRIP_CLOSE}",
        f"  GRIP_FORCE = {GRIP_FORCE}",
    ]) + "\n"


# ============================================================
# 3. PC 서버 (Day1 lecture3와 같은 방식: 로봇이 접속해서 "req_data"를 보내면 값으로 답함)
# ============================================================
def start_server():
    """로봇이 접속할 서버 열기"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))               # 127.0.0.1이면 로봇이 접속 못 함
    server.listen(1)
    server.settimeout(20)                        # 20초 안에 로봇이 안 오면 포기
    return server


def answer_robot(server, p_cam):
    """로봇의 "req_data"에 (x, y, z)로 답하기. x, y, z = 카메라 기준(m)"""
    try:
        conn, addr = server.accept()
    except socket.timeout:
        print("로봇이 접속하지 않았습니다. Remote 모드, PC_IP, 방화벽을 확인하세요.")
        return
    print(f"로봇 접속: {addr}")
    msg = conn.recv(1024).decode()
    if "req_data" in msg:
        reply = "(%.4f,%.4f,%.4f)" % (p_cam[0], p_cam[1], p_cam[2])
        conn.sendall(reply.encode())             # 끝에 \n 붙이지 않기 (Day1 lecture3 참고)
        print(f">> 보냄 {reply}")
    conn.close()


def pick_place(server, p_cam):
    """[그리퍼 정의 + 설정값 + 로봇 프로그램]을 보내고, 로봇의 질문에 답하기"""
    send(gripper_header() + settings_lines() + read_file(ROBOT_SCRIPT) + "end")
    print(">> 프로그램 보냄. 로봇이 접속하기를 기다리는 중...")
    answer_robot(server, p_cam)


# ============================================================
# 4. 카메라 (Day4와 같음)
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
# 5. 물체 고르기 (Day4 2단계와 같음, boxes → obb만 다름)
# ============================================================
def pick_target(result, names):
    """탐지 결과에서 TARGET 중 가장 확실한 박스 하나 고르기. 없으면 None"""
    best, best_conf = None, 0
    img_h, img_w = result.orig_shape                   # 화면 크기 (세로, 가로)
    for box in result.obb:
        name = names[int(box.cls[0])]
        conf = float(box.conf[0])
        if name != TARGET or conf < CONF_MIN:
            continue
        corners = box.xyxyxyxy[0].tolist()             # 꼭짓점 4개 [[x, y], ...]
        if any(not (0 <= x < img_w and 0 <= y < img_h) for x, y in corners):
            continue                                   # 화면 밖으로 잘린 물체는 빼기
        if conf > best_conf:
            best, best_conf = box, conf
    return best



# ============================================================
# 6. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe, align = start_camera()
    server = start_server()
    plan = None                                     # (u, v, 카메라 기준 점). 없으면 None

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
            if key == ord(" "):
                stop()
            if key == ord("c"):
                plan = None; print("취소")
            if key == ord("t"):
                if box is None:
                    print(f"{TARGET}을(를) 찾지 못했습니다.")
                else:
                    x, y, w, h, r = box.xywhr[0].tolist()       # 중심 x, y, 폭, 높이, 각도 (각도 r은 여기선 안 씀)
                    u, v = int(x), int(y)
                    p_cam = pixel_to_camera(u, v, depth, intr)
                    if p_cam is None:
                        print("깊이를 못 읽었습니다. 물체 위치를 바꿔 보세요.")
                    else:
                        plan = (u, v, p_cam)
                        print(f"{TARGET} 중심 ({u},{v})")
                        print(f"   카메라 기준 점 {np.round(p_cam*1000,1)} mm.  m=실행 / c=취소")
            if key == ord("m") and plan:
                pick_place(server, plan[2])
                plan = None
    except KeyboardInterrupt:
        stop()
    finally:
        server.close(); pipe.stop(); cv2.destroyAllWindows()


main()
