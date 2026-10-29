# 클릭한 점 위로 로봇 보내기 (카메라-툴 캘리브레이션 확인용)
# - 화면에서 점을 클릭 → 그 점의 30cm 위로 그리퍼 끝(TCP)이 가도록 목표를 계산해 보여줌
# - m = 이동, c = 취소, 스페이스 = 정지 명령, q = 종료
# - 자세(회전)는 지금 그대로 두고 위치만 바꿈. 펜던트는 원격제어(Remote) 모드
import socket, struct
import numpy as np, cv2, pyrealsense2 as rs


# ============================================================
# 1. 설정값
# ============================================================
ROBOT_IP = "192.168.1.104"
TCP_CAMERA = [-0.026, -0.056, -0.2197, 0, 0, 0]   # 툴(그리퍼 끝 TCP, z 238.7mm) 기준 카메라 위치·회전 (2026-10-19 마커 없는 캘리브레이션 결과, 플랜지 기준 z 0.019 - 0.2387)
HOVER = 0.30                                     # 점 위 높이(m)
SPEED_V, SPEED_A = 0.05, 0.2                     # 직선 이동 속도(m/s), 가속도


# ============================================================
# 2. 로봇 통신
# ============================================================
def read_pose():
    """30013 실시간 포트(읽기 전용)에서 현재 TCP 자세 [x, y, z, rx, ry, rz] 읽기"""
    s = socket.create_connection((ROBOT_IP, 30013), timeout=3)
    buf = b""
    while len(buf) < 4: buf += s.recv(4096)
    n = struct.unpack(">i", buf[:4])[0]
    while len(buf) < n: buf += s.recv(4096)
    s.close()
    d = struct.unpack(">%dd" % ((n - 4) // 8), buf[4:4 + ((n - 4) // 8) * 8])
    return np.array(d[55:61])


def send(script):
    """URScript 프로그램을 30002 포트로 보내기"""
    r = socket.create_connection((ROBOT_IP, 30002), timeout=3)
    r.sendall((script + "\n").encode()); r.close()


def move_to(target):
    """target 자세로 직선 이동(movel) 명령 보내기"""
    p = "p[%s]" % ", ".join("%.6f" % x for x in target)
    send(f"def click_move():\n  movel({p}, a={SPEED_A}, v={SPEED_V})\nend")
    print(">> 이동 명령 보냄:", p)


def stop():
    """정지 명령 보내기"""
    send("def stop_now():\n  stopl(0.5)\nend")
    print(">> 정지 명령 보냄")


# ============================================================
# 3. 카메라
# ============================================================
def start_camera():
    """RealSense 컬러 + 깊이 시작. (pipe, align) 반환"""
    pipe = rs.pipeline(); cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipe.start(cfg)
    align = rs.align(rs.stream.color)                # 깊이를 컬러 화면에 맞춰 정렬
    return pipe, align


def get_frame(pipe, align):
    """프레임 한 장 받기. (컬러 이미지, 깊이 프레임, 내부 파라미터) 반환"""
    f = align.process(pipe.wait_for_frames())
    color = np.asanyarray(f.get_color_frame().get_data())
    depth = f.get_depth_frame()
    intr = f.get_color_frame().profile.as_video_stream_profile().intrinsics
    return color, depth, intr


# ============================================================
# 4. 좌표 변환
# ============================================================
def pixel_to_camera(u, v, depth, intr):
    """픽셀 (u, v) → 카메라 기준 3D 점(m). 깊이를 못 읽으면 None"""
    z = depth.get_distance(u, v)                                        # 픽셀 (u, v)까지의 거리(m)
    if z <= 0:                                                          # 0이면 깊이를 못 읽은 것
        return None
    return np.array(rs.rs2_deproject_pixel_to_point(intr, [u, v], z))   # 픽셀(u, v) + 깊이(z) → 3D 점


def camera_to_base(p_cam, pose):
    """카메라 기준 점(m) → 로봇 베이스 기준 점(m)"""
    R_cam_to_tool, _ = cv2.Rodrigues(np.array(TCP_CAMERA[3:], dtype=float))   # 툴 기준 카메라 회전
    t_cam = np.array(TCP_CAMERA[:3])                                            # 툴 기준 카메라 위치
    R_tool_to_base, _ = cv2.Rodrigues(pose[3:])                                # 베이스 기준 툴 회전
    t_tool = pose[:3]                                                           # 베이스 기준 툴 위치
    p_tool = R_cam_to_tool @ p_cam + t_cam          # 카메라 → 툴
    return R_tool_to_base @ p_tool + t_tool         # 툴 → 베이스


def make_target(point, pose):
    """지금 자세(회전)는 그대로, 위치만 point의 HOVER 위로 바꾼 목표 자세"""
    target = pose.copy()
    target[:3] = point + [0, 0, HOVER]
    return target


# ============================================================
# 5. 메인
# ============================================================
clicked = []        # 마우스로 클릭한 픽셀 (u, v)가 여기 들어옴


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked.append((x, y))


def main():
    pipe, align = start_camera()
    cv2.namedWindow("click to move")
    cv2.setMouseCallback("click to move", on_mouse)
    target_info = None                              # (u, v, 목표 자세). 없으면 None

    try:
        while True:
            color, depth, intr = get_frame(pipe, align)

            # (1) 클릭했으면 목표 계산
            if clicked:
                u, v = clicked.pop()
                p_cam = pixel_to_camera(u, v, depth, intr)
                if p_cam is None:
                    print("깊이를 못 읽었습니다. 다른 점을 클릭하세요.")
                else:
                    pose = read_pose()
                    point = camera_to_base(p_cam, pose)
                    target = make_target(point, pose)
                    target_info = (u, v, target)
                    dist = np.linalg.norm(target[:3] - pose[:3]) * 1000
                    print(f"클릭 ({u},{v}) 깊이 {p_cam[2]*1000:.0f}mm → 베이스 점 {np.round(point*1000,1)} mm")
                    print(f"   목표(30cm 위) {np.round(target[:3]*1000,1)} mm, 이동 거리 {dist:.0f}mm.  m=이동 / c=취소")

            # (2) 화면 표시 (목표가 있으면 클릭한 곳에 + 표시)
            if target_info:
                u, v, _ = target_info
                cv2.drawMarker(color, (u, v), (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
            cv2.imshow("click to move", color)

            # (3) 키 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                stop()
            if key == ord("c"):
                target_info = None; print("취소")
            if key == ord("m") and target_info:
                move_to(target_info[2])
                target_info = None
    except KeyboardInterrupt:
        stop()
    finally:
        pipe.stop(); cv2.destroyAllWindows()


main()
