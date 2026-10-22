# 1단계: OBB(기울어진 박스) 출력 보기
# - Day4 1단계와 같은데, 박스가 기울어질 수 있음 → 각도 r이 하나 더 나옴
# - p = 지금 화면의 탐지 결과 출력, q = 종료
# - 실행: Session5_AI_robot 폴더에서 python answer/1_obb_output.py
import math
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
MODEL_PATH = "4_pick_and_place/weights/obb/best.pt"     # 도형 블록으로 학습한 OBB 모델


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
# 3. 메인
# ============================================================
def main():
    model = YOLO(MODEL_PATH)
    pipe = start_camera()

    try:
        while True:
            color = get_color(pipe)
            result = model(color, verbose=False)[0]

            cv2.imshow("obb output", result.plot())     # YOLO가 그려 준 그림 (기울어진 박스)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("p"):
                print(f"\n찾은 물체 수: {len(result.obb)}")
                for box in result.obb:
                    name = model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    x, y, w, h, r = box.xywhr[0]               # 중심 x, 중심 y, 폭, 높이, 각도(라디안)
                    deg = r * 180 / math.pi                     # 라디안 → 도 (π 라디안 = 180도)
                    print(f"  {name:10s} 신뢰도 {conf:.2f}  중심 ({x:.0f}, {y:.0f})  크기 {w:.0f}x{h:.0f}  각도 {deg:.1f}°")
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
