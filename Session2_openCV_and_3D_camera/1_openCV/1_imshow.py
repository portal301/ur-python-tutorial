import cv2

# 이미지 파일 경로
image_path = 'img/sample.jpg'

# 이미지를 컬러(BGR)로 불러오기
img = cv2.imread(image_path)

# 이미지가 잘 불러와졌는지 확인
if img is None:
    print("이미지를 불러오지 못했습니다.")
else:
    print("이미지 크기:", img.shape)  # (높이, 너비, 채널)

# 이미지 보여주기
cv2.imshow("Original Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
