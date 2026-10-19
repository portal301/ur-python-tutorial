from ultralytics import YOLO
import cv2

if __name__ == "__main__":
    # Load trained weights
    model = YOLO("runs/detect/train/weights/best.pt")

    # Open webcam (0번 카메라)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO 모델로 객체 탐지
        results = model(frame)

        # 결과 이미지 얻기
        annotated_frame = results[0].plot()

        # 화면에 표시
        cv2.imshow("YOLO Real-time Detection", annotated_frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()