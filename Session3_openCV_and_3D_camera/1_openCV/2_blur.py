import cv2
import matplotlib.pyplot as plt

# 파라미터 지정
ksize = 5               # 커널 크기 (홀수만 가능: 3, 5, 7, 9 ...)
sigma = 0               # Gaussian Blur용 sigmaX
bilateral_d = 9         # Bilateral 필터의 d
bilateral_sigma_color = 75
bilateral_sigma_space = 75

# 이미지 불러오기
img = cv2.imread('img/sample.jpg')
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # matplotlib 출력용

# 평균 블러 (Average Blur)
blur_avg = cv2.blur(img, (ksize, ksize))

# 가우시안 블러
blur_gauss = cv2.GaussianBlur(img, (ksize, ksize), sigma)

# 미디안 블러 (ksize는 홀수만 가능)
if ksize % 2 == 1:
    blur_median = cv2.medianBlur(img, ksize)
else:
    raise ValueError("MedianBlur requires an odd ksize (3, 5, 7, ...).")

# 양방향 필터
blur_bilateral = cv2.bilateralFilter(
    img, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)

# RGB로 변환 
blur_avg_rgb = cv2.cvtColor(blur_avg, cv2.COLOR_BGR2RGB)
blur_gauss_rgb = cv2.cvtColor(blur_gauss, cv2.COLOR_BGR2RGB)
blur_median_rgb = cv2.cvtColor(blur_median, cv2.COLOR_BGR2RGB)
blur_bilateral_rgb = cv2.cvtColor(blur_bilateral, cv2.COLOR_BGR2RGB)

#  시각화 
titles = [
    f"Original",
    f"Average Blur ({ksize}x{ksize})",
    f"Gaussian Blur ({ksize}x{ksize}, σ={sigma})",
    f"Median Blur (ksize={ksize})",
    f"Bilateral Filter (d={bilateral_d})"
]
images = [
    img_rgb,
    blur_avg_rgb,
    blur_gauss_rgb,
    blur_median_rgb,
    blur_bilateral_rgb
]

plt.figure(figsize=(9, 6))

for i in range(5):
    plt.subplot(2, 3, i + 1)
    plt.imshow(images[i])
    plt.title(titles[i], fontsize=10)
    plt.axis('off')

plt.tight_layout()
plt.show()
