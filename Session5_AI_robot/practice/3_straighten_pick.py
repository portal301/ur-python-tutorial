# 3단계: 삐뚤어진 물체를 집어서 똑바로 내려놓기
# - Day4 4단계(YOLO로 찾은 물체 위로 이동)에 손목 회전과 집기·놓기 순서를 더함
# - 순서: 물체 위 → 손목을 a만큼 돌림 → 내려감 → 잡기 → 올라옴 → 손목을 원래대로 → 내려감 → 놓기 → 올라옴
#   (잡은 채로 손목을 원래대로 돌리면 물체가 -a만큼 돌아서 똑바로 섬)
# - t = 목표 계산, m = 실행, c = 취소, 스페이스 = 정지 명령, q = 종료
# - 그리퍼(잡기·놓기)는 아직 빈칸: 메시지만 띄우고 1초 기다림
# - 실행: Session5_AI_robot 폴더에서 python practice/3_straighten_pick.py
import math, socket, struct
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
ROBOT_IP = "192.168.0.110"
TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전 (Day3와 같음, 플랜지 기준 z 0.019 - 0.2387)
HOVER = 0.30                                     # 물체 위 높이(m)
GRASP_ABOVE = 0.05                               # 물체 윗면에서 이만큼 위까지만 내려감(m). 강의장에서 그리퍼에 맞춰 조정
SPEED_V, SPEED_A = 0.05, 0.2                     # 직선 이동 속도(m/s), 가속도
MODEL_PATH = "4_pick_and_place/weights/obb/best.pt"
TARGET = "square"
CONF_MIN = 0.5


# ============================================================
# 2. 로봇 통신 (Day4와 같음)
# ============================================================
def read_pose():
    """30013 실시간 포트(읽기 전용)에서 현재 TCP 자세 [x, y, z, rx, ry, rz] 읽기"""
    s = socket.create_connection((ROBOT_IP, 30013), timeout=3)
    buf = b""
    while len(buf) < 4: buf += s.recv(4096)
    n = struct.unpack(">i", buf[:4])[0]
    while len(buf) < n: buf += s.recv(4096)
    s.close()
    d = struct.unpack(">%dd" % ((n - 4) // 8), buf[4:4 + ((n - 4) // 8) * 8])
    return np.array(d[55:61])


def send(script):
    """URScript 프로그램을 30002 포트로 보내기"""
    r = socket.create_connection((ROBOT_IP, 30002), timeout=3)
    r.sendall((script + "\n").encode()); r.close()


def stop():
    """정지 명령 보내기"""
    send("def stop_now():\n  stopl(0.5)\nend")
    print(">> 정지 명령 보냄")


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


# ============================================================
# 4. 물체 고르기·각도 (1·2단계와 같음)
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


def straighten_angle(deg):
    """물체 각도(도) → 똑바로 세우려면 돌려야 할 가장 작은 각도(도, -45 ~ 45)"""
    return (deg + 45) % 90 - 45


# ============================================================
# 5. 좌표 변환 (Day4와 같음 + 손목 회전)
# ============================================================
def pixel_to_camera(u, v, depth, intr):
    """픽셀 (u, v) → 카메라 기준 3D 점(m). 깊이를 못 읽으면 None"""
    z = depth.get_distance(u, v)
    if z <= 0:
        return None
    return np.array(rs.rs2_deproject_pixel_to_point(intr, [u, v], z))


def camera_to_base(p_cam, pose):
    """카메라 기준 점(m) → 로봇 베이스 기준 점(m)"""
    R_cam_to_tool, _ = cv2.Rodrigues(np.array(TCP_CAMERA[3:], dtype=float))
    p_tool = R_cam_to_tool @ p_cam + np.array(TCP_CAMERA[:3])
    R_tool_to_base, _ = cv2.Rodrigues(pose[3:])
    return R_tool_to_base @ p_tool + pose[:3]


def rotate_tool_z(pose, deg):
    """pose를 툴의 z축(손목 축) 기준으로 deg만큼 돌린 자세"""
    R, _ = cv2.Rodrigues(pose[3:])
    t = math.radians(deg)
    Rz = np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])
    rv, _ = cv2.Rodrigues(R @ Rz)
    out = pose.copy()
    out[3:] = rv.flatten()
    return out


def make_poses(point, pose, a):
    """집고 놓는 데 필요한 자세 4개 만들기"""
    hover = pose.copy()
    hover[:3] = point + [0, 0, HOVER]                # 물체 위, 손목은 지금 그대로
    down = hover.copy()
    down[2] = point[2] + GRASP_ABOVE                 # 내려간 자리, 손목 그대로
    # TODO 1: 손목을 a만큼 돌린 자세 2개 만들기
    hover_rot = ____                                 # 물체 위, 손목을 a만큼 돌림
    down_rot = ____                                  # 내려간 자리, 손목을 a만큼 돌림
    return hover, down, hover_rot, down_rot


# ============================================================
# 6. 집고 똑바로 놓기
# ============================================================
def movel(pose):
    return "  movel(p[%s], a=%s, v=%s)" % (", ".join("%.6f" % x for x in pose), SPEED_A, SPEED_V)


def grip(msg):
    """그리퍼 자리 (RG2-FT 함수로 바꿀 곳)"""
    return f'  textmsg("{msg}")\n  sleep(1.0)'


def straighten_pick(hover, down, hover_rot, down_rot):
    """집기 → 손목 되돌리기 → 놓기 순서를 URScript 프로그램 하나로 보내기"""
    lines = [
        # TODO 2: 맨 위 주석의 순서대로 movel(자세) / grip("...")을 채우기
        ____,                   # 물체 위로
        ____,                   # 손목을 물체에 맞춰 돌림
        ____,                   # 내려감
        ____,                   # 잡기
        ____,                   # 올라옴
        ____,                   # 손목을 원래대로 → 물체가 똑바로 섬
        ____,                   # 내려감
        ____,                   # 놓기
        ____,                   # 올라옴
    ]
    send("def straighten_pick():\n" + "\n".join(lines) + "\nend")
    print(">> 집고 똑바로 놓기 명령 보냄")


# ============================================================
# 7. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe, align = start_camera()
    plan = None                                     # (u, v, 자세 4개). 없으면 None

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
            cv2.imshow("straighten pick", color)

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
                    x, y, w, h, r = box.xywhr[0].tolist()
                    u, v = int(x), int(y)
                    # TODO 3: 손목을 돌릴 각도 (2단계 참고)
                    a = ____
                    p_cam = pixel_to_camera(u, v, depth, intr)
                    if p_cam is None:
                        print("깊이를 못 읽었습니다. 물체 위치를 바꿔 보세요.")
                    else:
                        pose = read_pose()
                        point = camera_to_base(p_cam, pose)
                        plan = (u, v, make_poses(point, pose, a))
                        print(f"{TARGET} 중심 ({u},{v}) 각도 {math.degrees(r):.1f}° → 손목 {a:+.1f}° 회전")
                        print(f"   베이스 점 {np.round(point*1000,1)} mm.  m=실행 / c=취소")
            if key == ord("m") and plan:
                straighten_pick(*plan[2])
                plan = None
    except KeyboardInterrupt:
        stop()
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
