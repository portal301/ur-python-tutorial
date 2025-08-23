import pyrealsense2 as rs
import numpy as np
import cv2

# 1. RealSense 파이프라인 설정
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile = pipe.start(cfg)

# 2. RGB 영상과 Depth 영상을 정렬
align = rs.align(rs.stream.color)

# 3. 초기 프레임 수신 및 Intrinsics 추출
for _ in range(5):  # 안정화
    frames = pipe.wait_for_frames()
aligned_frames = align.process(frames)
depth_frame = aligned_frames.get_depth_frame()
depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics

# 4. 클릭 시 해당 픽셀의 3D 위치 출력 함수
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        aligned_frames = align.process(pipe.wait_for_frames())
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame:
            print("⚠️ Depth frame not available.")
            return

        depth = depth_frame.get_distance(x, y)
        point_3d = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], depth)

        print(f"\n Clicked Pixel: ({x}, {y})")
        print(f" → Depth (Z): {depth:.3f} m")
        print(f" → 3D Position [X, Y, Z] (m): {point_3d}")

# 5. 마우스 콜백 등록
cv2.namedWindow('RGB Image')
cv2.setMouseCallback('RGB Image', mouse_callback)

# 6. 메인 루프
try:
    while True:
        frames = pipe.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        depth_cm = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.5), cv2.COLORMAP_JET
        )

        cv2.imshow('RGB Image', color_image)
        cv2.imshow('Depth Map', depth_cm)

        if cv2.waitKey(1) == ord('q'):
            break

        # X 버튼 눌러도 종료
        if (cv2.getWindowProperty('RGB Image', cv2.WND_PROP_VISIBLE) < 1 or
            cv2.getWindowProperty('Depth Map', cv2.WND_PROP_VISIBLE) < 1):
            break

finally:
    pipe.stop()
    cv2.destroyAllWindows()
