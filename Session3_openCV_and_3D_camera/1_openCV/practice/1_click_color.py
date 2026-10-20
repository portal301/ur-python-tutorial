import cv2

# 1. 이미지 불러오기
img = cv2.imread('img/shapes_512.jpg')


# 2. 마우스를 클릭하면 자동으로 실행되는 함수
def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:          # 왼쪽 버튼을 눌렀을 때
        # TODO 1: 클릭한 픽셀의 색 읽기
        b, g, r = ____
        print(f"클릭 위치 (x={x}, y={y})  색 B={b}, G={g}, R={r}")

        # TODO 2: 클릭한 곳 주변 10x10 픽셀(y0~y1, x0~x1)을 빨간색으로 칠하기
        y0, y1 = max(0, y - 5), min(img.shape[0], y + 5)
        x0, x1 = max(0, x - 5), min(img.shape[1], x + 5)
        ____ = (0, 0, 255)

        # 바뀐 이미지 다시 보여주기
        cv2.imshow("Click", img)


# 3. 창을 띄우고, 마우스 함수 연결하기
cv2.imshow("Click", img)
cv2.setMouseCallback("Click", on_mouse)

cv2.waitKey(0)
cv2.destroyAllWindows()
