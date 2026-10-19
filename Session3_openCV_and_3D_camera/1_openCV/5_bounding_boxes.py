import cv2
import matplotlib.pyplot as plt

# 1. 이미지 불러오기
img = cv2.imread('img/shapes.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. Gaussian Blur + Canny Edge
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)

# 3. 컨투어 추출
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 4. Bounding Box 및 Rotated Bounding Box 그리기
img_bbox = img.copy()
for contour in contours:
    # 일반 bounding box (빨간색)
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img_bbox, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 회전된 bounding box (초록색)
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = box.astype(int)
    cv2.drawContours(img_bbox, [box], 0, (0, 255, 0), 2)

# 5. RGB 변환
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_bbox_rgb = cv2.cvtColor(img_bbox, cv2.COLOR_BGR2RGB)

# 7. 시각화 (subplot)
plt.figure(figsize=(10,5))

plt.subplot(1, 2, 1)
plt.imshow(img_rgb)
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(img_bbox_rgb)
plt.title("Bounding Boxes")
plt.axis("off")

plt.tight_layout()
plt.show()
