# 3단계: 얼마나 돌리면 똑바로 서는지 구하기
# - 사각형은 90°마다 같은 모양 → 30°나 120°나 똑바로 세우려면 30°만 돌리면 됨
# - 그래서 각도를 -45° ~ 45° 사이로 맞추면 "가장 적게 돌리는 각도"가 됨
# - 초록 = 지금 박스, 노랑 = 그만큼 돌려서 똑바로 세운 모습. q = 종료
# - 실행: Session5_AI_robot 폴더에서 python answer/3_straighten_angle.py
import math
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
MODEL_PATH = ""
TARGET = ""                                          # 찾을 물체 이름
CONF_MIN = 0.5


# ============================================================
# 2. 카메라
# ============================================================
def start_camera():
    """RealSense 컬러 시작"""
    pipe = rs.pipeline(); cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipe.start(cfg)
    return pipe


def get_color(pipe):
    """컬러 이미지 한 장 받기"""
    f = pipe.wait_for_frames()
    return np.asanyarray(f.get_color_frame().get_data())


# ============================================================
# 3. 물체 고르기 (Day4 2단계와 같음, boxes → obb만 다름)
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
# 4. 똑바로 세우는 각도
# ============================================================
def straighten_angle(deg):
    """물체 각도(도) → 똑바로 세우려면 돌려야 할 가장 작은 각도(도, -45 ~ 45)"""
    return (deg + 45) % 90 - 45


def rotate_points(points, cx, cy, deg):
    """점들을 중심 (cx, cy) 기준으로 deg만큼 돌리기 (화면 좌표 기준)"""
    t = math.radians(deg)
    R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
    center = np.array([cx, cy])
    return (points - center) @ R.T + center


# ============================================================
# 5. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe = start_camera()

    try:
        while True:
            color = get_color(pipe)
            result = model(color, verbose=False)[0]
            box = pick_target(result, model.names)

            if box is not None:
                x, y, w, h, r = box.xywhr[0].tolist()
                a = straighten_angle(math.degrees(r))               # 돌릴 각도
                corners = np.array(box.xyxyxyxy[0].tolist())
                straight = rotate_points(corners, x, y, -a)   # a만큼 되돌리면 똑바로 섬

                cv2.polylines(color, [corners.astype(int)], True, (0, 255, 0), 2)
                cv2.polylines(color, [straight.astype(int)], True, (0, 255, 255), 2)
                cv2.putText(color, f"{TARGET} {math.degrees(r):.1f} deg -> turn {a:+.1f} deg",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow("straighten angle", color)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
