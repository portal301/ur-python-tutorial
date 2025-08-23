import cv2
import numpy as np
import os
import glob
import json

# JSON 파일에서 camera intrinsic 불러오기
with open(os.path.join("camera_params", "camera_intrinsic.json"), "r") as f:
    data = json.load(f)
    camera_matrix = np.array(data["camera_matrix"])
    dist_coeffs = np.array(data["dist_coeff"])

# 보정할 이미지 폴더
input_dir = os.path.join("camera_params", "calibration_data")
output_dir = os.path.join("camera_params", "undistorted")
os.makedirs(output_dir, exist_ok=True)

# 이미지 목록 불러오기
image_paths = glob.glob(os.path.join(input_dir, "*.jpg"))

for image_path in image_paths:
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    # 최적화된 보정 카메라 매트릭스 구하기
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (w, h), 1, (w, h)
    )

    # 왜곡 제거
    undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # ROI로 잘라내기 (선택 사항)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]

    # 저장
    filename = os.path.basename(image_path)
    save_path = os.path.join(output_dir, filename)
    cv2.imwrite(save_path, undistorted_img)
    print(f"Saved: {save_path}")
