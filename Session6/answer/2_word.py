# 미션 2: 단어 만들기 - WORD에 적힌 순서(예: MR obb obb MR)대로 물체를 칸에 놓기
# - 1단계와 같은데, 글자마다 맞는 물체를 골라야 함 (같은 물체를 두 번 고르면 안 됨)
# - 집는 구역(카메라에 보이는 곳)과 놓을 칸(SLOT)은 서로 다른 구역에 둠
# - 물체 하나마다: 물체 위 → 손목 a만큼 돌림 → 내려감 → 잡기 → 올라옴
#                → 놓을 칸 위(손목 원래대로) → 내려감 → 놓기 → 올라옴
# - t = 목표 계산, m = 실행, c = 취소, 스페이스 = 정지, q = 종료
# - 그리퍼: Day2 스크립트의 OnRobot 정의를 앞에 붙여 rg2ft_grip으로 잡기·놓기
# - 실행: Session6 폴더에서 python answer/2_word.py
import math, socket, struct
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
ROBOT_IP = "192.168.0.3"
TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전 (Day3와 같음, 플랜지 기준 z 0.019 - 0.2387)
HOVER = 0.30                                     # 물체 위 높이(m)
TOOL_DOWN = [0.0611, 3.141, 0.0]                 # 툴이 정확히 아래(베이스 -z)를 보는 회전 rx, ry, rz. 집을 때 이 회전을 씀. 강의장에서 다시 재기
GRASP_OFFSET = [0.0, 0.0, 0.05]                  # 물체 윗면 기준 잡는 위치 보정 x, y, z(m, 베이스 기준으로 더함). z가 음수면 더 내려감. 강의장에서 그리퍼에 맞춰 조정
SPEED_V, SPEED_A = 0.05, 0.2                     # 직선 이동 속도(m/s), 가속도
MODEL_PATH = ""                                 # OBB 모델 경로
CLASSES = ()                          # 모델의 클래스 이름과 같아야 함 (MR 물체, obb = AI 물체)
CONF_MIN = 0.5
GRIPPER_SCRIPT = "../Session2_gripper_urcaps/answer/gripper_open_close.script"   # Day2 그리퍼 스크립트 (위쪽 OnRobot 정의만 가져다 씀)
GRIP_OPEN, GRIP_CLOSE, GRIP_FORCE = 100.0, 20.0, 40.0                         # 그리퍼 열기·닫기 폭(mm), 힘(N)

WORD = []                # 만들 단어 (클래스 이름을 차례대로)
SLOT_START = [0.40, -0.20]                       # TODO 직접 재기!! 첫 번째 놓을 칸의 베이스 기준 x, y(m) (티치펜던트로 칸 위에 TCP를 두고 읽은 값)
SLOT_GAP = [0.0, 0.08]                           # TODO 직접 재기!! 칸 사이 간격 x, y(m) (물체가 서로 안 닿게)


# ============================================================
# 2. 로봇 통신 (Day5와 같음)
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


# ============================================================
# 3. 카메라 (Day5와 같음)
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
# 4. 좌표 변환·손목 회전 (Day5와 같음)
# ============================================================
def straighten_angle(deg):
    """물체 각도(도) → 똑바로 세우려면 돌려야 할 가장 작은 각도(도, -45 ~ 45)"""
    return (deg + 45) % 90 - 45


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


# ============================================================
# 5. 물체 전부 찾기 (새로 추가)
# ============================================================
def find_objects(result, names, depth, intr, pose):
    """화면 속 물체(CLASSES)를 전부 찾아서 목록으로 반환.
    물체 하나 = {"name": 클래스 이름, "u": 픽셀 x, "v": 픽셀 y, "a": 손목 회전 각도, "point": 베이스 기준 점}"""
    objects = []
    for box in result.obb:
        name = names[int(box.cls[0])]
        if name not in CLASSES or float(box.conf[0]) < CONF_MIN:
            continue
        x, y, w, h, r = box.xywhr[0].tolist()
        u, v = int(x), int(y)
        p_cam = pixel_to_camera(u, v, depth, intr)
        if p_cam is None:
            continue                                # 깊이를 못 읽은 물체는 건너뜀
        objects.append({
            "name": name, "u": u, "v": v,
            "a": straighten_angle(math.degrees(r)),
            "point": camera_to_base(p_cam, pose),
        })
    return objects


# ============================================================
# 6. 놓을 칸·순서 정하기 (새로 추가)
# ============================================================
def slot_xy(i):
    """i번째 놓을 칸의 베이스 기준 x, y(m)"""
    return [SLOT_START[0] + i * SLOT_GAP[0], SLOT_START[1] + i * SLOT_GAP[1]]


def make_plan(word, objects):
    """WORD의 이름마다 맞는 물체를 하나씩 골라 [(물체, 칸 번호), ...]로 반환. 모자라면 None"""
    plan = []
    used = set()                                    # 이미 고른 물체 번호 (같은 물체를 두 번 고르지 않도록)
    for i, letter in enumerate(word):         # letter = 클래스 이름 하나 (예: "MR")
        found = None                                # 고른 물체 번호
        for j, obj in enumerate(objects):
            if obj["name"] == letter and j not in used:
                found = j
                break
        if found is None:
            print(f"'{letter}' 물체가 모자랍니다.")
            return None
        used.add(found)
        plan.append((objects[found], i))
    return plan


# ============================================================
# 7. 집고 칸에 놓기
# ============================================================
def movel(pose):
    return "  movel(p[%s], a=%s, v=%s)" % (", ".join("%.6f" % x for x in pose), SPEED_A, SPEED_V)


def grip(width):
    """그리퍼를 width(mm)만큼 벌리거나 좁히는 URScript 줄 (RG2-FT)"""
    return f"  rg2ft_grip({width}, {GRIP_FORCE}, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)"


def gripper_header():
    """Day2 그리퍼 스크립트에서 OnRobot 정의 부분(본문 앞까지)만 읽어 오기"""
    with open(GRIPPER_SCRIPT, encoding="utf-8") as file:
        text = file.read()
    mark = "  # end: URCap Installation Node\n"
    return text.rsplit(mark, 1)[0] + mark          # 마지막 경계 줄까지 (앞쪽 다른 URCap에도 같은 줄이 있음)


def pick_place_lines(obj, slot, pose):
    """물체 하나를 집어서 slot번 칸에 똑바로 놓는 URScript 줄들"""
    p = obj["point"]
    hover = pose.copy(); hover[:3] = p + [0, 0, HOVER]           # 물체 위
    hover[3:] = TOOL_DOWN                                        # 툴은 정확히 아래를 봄
    down = hover.copy(); down[:3] = p + GRASP_OFFSET             # 물체까지 내려간 자리 (보정 더함)
    hover_rot = rotate_tool_z(hover, obj["a"])                   # 물체 위, 손목을 a만큼 돌림
    down_rot = rotate_tool_z(down, obj["a"])                     # 내려간 자리, 손목을 a만큼 돌림

    sx, sy = slot_xy(slot)
    slot_hover = hover.copy(); slot_hover[0], slot_hover[1] = sx, sy   # 칸 위, 손목 원래대로
    slot_down = down.copy(); slot_down[0], slot_down[1] = sx, sy       # 칸까지 내려간 자리 (집을 때와 같은 높이)
    return [
        movel(hover), movel(hover_rot), movel(down_rot), grip(GRIP_CLOSE), movel(hover_rot),
        movel(slot_hover), movel(slot_down), grip(GRIP_OPEN), movel(slot_hover),
    ]


def run_plan(plan, pose):
    """계획 전체를 URScript 프로그램 하나로 보내기"""
    lines = [grip(GRIP_OPEN)]                                    # 처음에 그리퍼부터 열어 둠 (닫힌 채로 내려가지 않도록)
    for obj, slot in plan:
        lines += pick_place_lines(obj, slot, pose)
    lines.append(movel(pose))                                    # 끝나면 처음 자세로 돌아옴
    send(gripper_header() + "\n".join(lines) + "\nend")   # OnRobot 정의 + 미션 동작
    print(f">> {len(plan)}개 옮기기 명령 보냄")


# ============================================================
# 8. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe, align = start_camera()
    plan, plan_pose = None, None

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)
            result = model(color, verbose=False)[0]

            for box in result.obb:                                 # 찾은 박스 그리기
                name = model.names[int(box.cls[0])]
                if name in CLASSES and float(box.conf[0]) >= CONF_MIN:
                    corners = np.array(box.xyxyxyxy[0].tolist(), dtype=np.int32)
                    cv2.polylines(color, [corners], True, (0, 255, 0), 2)
                    cv2.putText(color, name, tuple(corners[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if plan:                                               # 계획 순서 번호 표시
                for obj, slot in plan:
                    cv2.putText(color, str(slot + 1), (obj["u"], obj["v"]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(color, "WORD: " + " ".join(WORD), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow("mission", color)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                stop()
            if key == ord("c"):
                plan = None; print("취소")
            if key == ord("t"):
                pose = read_pose()
                objects = find_objects(result, model.names, depth, intr, pose)
                plan = make_plan(WORD, objects)
                plan_pose = pose
                if plan:
                    for obj, slot in plan:
                        print(f"  {obj['name']} ({obj['u']},{obj['v']}) 손목 {obj['a']:+.1f}° → {slot + 1}번 칸")
                    print("m=실행 / c=취소")
            if key == ord("m") and plan:
                run_plan(plan, plan_pose)
                plan = None
    except KeyboardInterrupt:
        stop()
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
