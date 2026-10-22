# 2단계: 탐지 결과에서 로봇이 갈 물체 하나 고르기
# - 마우스 클릭은 사람이 "무엇을, 어느 것을, 믿을 만한지, 어디를" 판단해서 찍음
# - 이 판단을 코드로 바꿔서, 고른 물체의 중심에 + 표시
# - q = 종료
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
MODEL_PATH = "yolo11n.pt"                        # COCO 사전학습 모델
TARGET = "cup"                                   # 찾을 물체 이름 (COCO 클래스 이름)
CONF_MIN = 0.5                                   # 이보다 신뢰도가 낮으면 무시


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
# 3. 물체 고르기
# ============================================================
def pick_target(result, names):
    """탐지 결과에서 로봇이 갈 박스 하나 고르기. 없으면 None"""
    best, best_conf = None, 0
    for box in result.boxes:
        name = names[int(box.cls[0])]
        conf = float(box.conf[0])
        if name != TARGET:                          # 무엇을: 찾는 물체가 아니면 건너뛰기
            continue
        if conf < CONF_MIN:                         # 믿을 만한가: 신뢰도가 낮으면 건너뛰기
            continue
        if conf > best_conf:                        # 어느 것을: 여러 개면 신뢰도가 가장 높은 것
            best, best_conf = box, conf
    return best


# ============================================================
# 4. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe = start_camera()

    try:
        while True:
            color = get_color(pipe)
            result = model(color, verbose=False)[0]
            view = result.plot()                        # YOLO가 찾은 것 전부

            box = pick_target(result, model.names)
            if box is not None:
                u, v = map(int, box.xywh[0][:2].tolist())   # 어디를: 박스 중심 (u, v)
                cv2.drawMarker(view, (u, v), (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
            cv2.imshow("pick target", view)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
