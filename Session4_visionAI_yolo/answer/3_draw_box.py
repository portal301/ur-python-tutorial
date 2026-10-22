# 3단계: 고른 물체를 cv2로 직접 그리기
# - YOLO가 그려 준 그림(result.plot()) 대신, 로봇이 갈 물체 하나만 직접 그림
# - 로봇을 움직이기 전에 "AI가 무엇을 골랐는지" 사람이 확인하기 위함
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
# 3. 물체 고르기 (2단계와 같음)
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


# ============================================================
# 4. 그리기
# ============================================================
def draw_target(img, box, names):
    """고른 박스, 이름·신뢰도, 중심을 img 위에 그리기"""
    x, y, w, h = box.xywh[0].tolist()                  # 중심 x, 중심 y, 폭, 높이 (1단계에서 본 값)
    x1, y1 = int(x - w / 2), int(y - h / 2)            # 왼쪽 위 = 중심에서 폭·높이의 절반만큼 빼기
    x2, y2 = int(x + w / 2), int(y + h / 2)            # 오른쪽 아래 = 중심에서 폭·높이의 절반만큼 더하기
    label = f"{names[int(box.cls[0])]} {float(box.conf[0]):.2f}"
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)                                  # 박스
    cv2.putText(img, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)   # 이름·신뢰도
    cv2.drawMarker(img, (int(x), int(y)), (0, 0, 255), cv2.MARKER_CROSS, 24, 2)             # 중심


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
                draw_target(color, box, model.names)
            cv2.imshow("draw box", color)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
