import cv2
import matplotlib.pyplot as plt

# 1. 이미지 불러오기
img = cv2.imread('img/sample.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. 가우시안 블러로 노이즈 제거
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 3. Canny 엣지 검출
edges = cv2.Canny(blur, 50, 150)

# 4. 시각화
plt.figure(figsize=(8, 4))

plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(edges, cmap='gray')
plt.title("Canny Edges")
plt.axis("off")

plt.tight_layout()
plt.show()
