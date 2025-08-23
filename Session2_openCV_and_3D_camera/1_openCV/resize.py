import cv2

# 1. 이미지 불러오기
img = cv2.imread('img/shapes.jpg')

# 2. 512x512로 리사이즈
resized = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

# 3. 저장 경로 설정 (원래 파일명에서 "_512" 추가)
save_path = 'img/sample_512.jpg'
cv2.imwrite(save_path, resized)

print(f"Resized image saved to {save_path}")
