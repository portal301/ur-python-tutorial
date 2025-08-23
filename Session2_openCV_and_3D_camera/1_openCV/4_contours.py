import cv2
import matplotlib.pyplot as plt

# 이미지 불러오기
img = cv2.imread('img/sample.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 가우시안 블러로 노이즈 제거
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Canny 엣지 검출
edges = cv2.Canny(blur, 50, 150)

# 컨투어 추출
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 파랑색 (BGR: 180, 100, 50)으로 컨투어 그리기
img_contour = img.copy()
contour_color = (180, 100, 50)
cv2.drawContours(img_contour, contours, -1, contour_color, 2)

# 시각화 (RGB로 변환해서 matplotlib으로 표시)
img_contour_rgb = cv2.cvtColor(img_contour, cv2.COLOR_BGR2RGB)
plt.imshow(img_contour_rgb)
plt.title("Contours (Blue)")
plt.axis("off")
plt.show()
