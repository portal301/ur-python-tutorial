import cv2
import numpy as np
import matplotlib.pyplot as plt

threshold = 30          # 밝기 차이가 이 값보다 크면 엣지로 판단

# 1. 이미지 불러오기 + 흑백 변환
img = cv2.imread('1_openCV/img/shapes_512.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
height, width = gray.shape

# 2. 결과를 담을 검은 이미지 (모든 픽셀 0)
my_edges = np.zeros((height, width), dtype=np.uint8)

# 3. 모든 픽셀을 돌면서 오른쪽 / 아래쪽 픽셀과 밝기 비교
for y in range(height - 1):
    for x in range(width - 1):
        # int()로 바꾸지 않으면 10 - 20 이 -10 이 아니라 246 이 됩니다 (uint8: 0~255)
        diff_x = abs(int(gray[y, x]) - int(gray[y, x + 1]))   # 오른쪽 픽셀과 차이
        diff_y = abs(int(gray[y, x]) - int(gray[y + 1, x]))   # 아래쪽 픽셀과 차이

        if diff_x > threshold or diff_y > threshold:
            my_edges[y, x] = 255                              # 흰색 = 엣지

# 4. 시각화
plt.figure(figsize=(8, 4))

plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(my_edges, cmap='gray')
plt.title(f"My Edges (threshold={threshold})")
plt.axis("off")

plt.tight_layout()
plt.show()
