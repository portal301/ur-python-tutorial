import pyrealsense2 as rs
import numpy as np
import cv2

pipe = rs.pipeline()
cfg = rs.config()

cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

pipe.start(cfg)

try:
    while True:
        frame = pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()
        color_frame = frame.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        depth_cm = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.5), 
            cv2.COLORMAP_JET
        )

        cv2.imshow('RGB Image', color_image)
        cv2.imshow('Depth Map', depth_cm)

        # 사용자가 'q' 키를 누르거나 창 X 버튼을 누르면 종료
        if cv2.waitKey(1) == ord('q'):
            break
        if (cv2.getWindowProperty('RGB Image', cv2.WND_PROP_VISIBLE) < 1 or
            cv2.getWindowProperty('Depth Map', cv2.WND_PROP_VISIBLE) < 1):
            break

finally:
    pipe.stop()
    cv2.destroyAllWindows()
