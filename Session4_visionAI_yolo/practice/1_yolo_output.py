# 1단계: YOLO 출력 형태 보기
# - 카메라 화면을 YOLO로 탐지하고, 결과 안에 어떤 숫자가 들어 있는지 출력해 봄
# - p = 지금 화면의 탐지 결과 출력, q = 종료
import numpy as np, cv2, pyrealsense2 as rs
from ultralytics import YOLO


# ============================================================
# 1. 설정값
# ============================================================
MODEL_PATH = "yolo11n.pt"                        # COCO 사전학습 모델


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
    # TODO 1: MODEL_PATH로 YOLO 모델 불러오기
    model = ____
    pipe = start_camera()

    try:
        while True:
            color = get_color(pipe)
            # TODO 2: color 이미지를 탐지하고, 결과 리스트의 첫 번째([0]) 꺼내기  (verbose=False: 로그 끄기)
            result = ____
            cv2.imshow("yolo output", result.plot())    # YOLO가 그려 준 그림

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("p"):
                print(f"\n찾은 물체 수: {len(result.boxes)}")
                for box in result.boxes:
                    # TODO 3: 박스에서 이름, 신뢰도, 중심·크기 꺼내기
                    #   값마다 [0]을 붙여 꺼냄 (박스 하나당 값이 1개 든 리스트라서)
                    name = ____                             # 클래스 번호 → 이름  (model.names[int(번호)])
                    conf = ____                             # 신뢰도 (0~1)
                    x, y, w, h = ____                       # 중심 x, 중심 y, 폭, 높이 (픽셀)
                    print(f"  {name:12s} 신뢰도 {conf:.2f}  중심 ({x:.0f}, {y:.0f})  크기 {w:.0f}x{h:.0f}")
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
