import cv2

tolerance = 40          # 클릭한 색에서 B, G, R 각각 ±이 값까지 "비슷한 색"으로 판단

# 1. 이미지 불러오기
img = cv2.imread('img/shapes_512.jpg')


# 2. 마우스를 클릭하면 자동으로 실행되는 함수
def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # 클릭한 픽셀의 색 읽기 (B, G, R)
        b, g, r = img[y, x]
        print(f"클릭 위치 (x={x}, y={y})  색 B={b}, G={g}, R={r}")
        color = [int(b), int(g), int(r)]        # int로 바꿔야 빼기/더하기 할 때 0~255를 넘어도 안전

        # 비슷한 색의 범위 정하기 (0~255 밖으로 나가지 않게 max / min)
        lower = []
        upper = []
        for c in color:
            lower.append(max(0, c - tolerance))
            upper.append(min(255, c + tolerance))

        # TODO 1: 이중 for문으로 모든 픽셀을 돌면서, B, G, R이 모두 lower~upper 안에 드는 픽셀 위치를 found에 넣기
        found = []
        for py in range(img.shape[0]):
            for px in range(img.shape[1]):
                pb, pg, pr = img[py, px]
                if ____:
                    found.append((px, py))

        # TODO 2: 원본은 그대로 두고, 복사본에서 찾은 픽셀만 빨간색으로 칠하기
        result = img.copy()
        for (px, py) in found:
            ____

        cv2.imshow("Click", result)


# 3. 창을 띄우고, 마우스 함수 연결하기
cv2.imshow("Click", img)
cv2.setMouseCallback("Click", on_mouse)

cv2.waitKey(0)
cv2.destroyAllWindows()
