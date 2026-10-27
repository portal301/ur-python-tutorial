# Lecture 4: Pick and Place

본 강의에서는 훈련시킨 YOLO 모델과 그리퍼를 이용하여 직접 `Pick and Place`를 구현해봅니다. 넓은 범위에서 물체를 감지하고 원하는 물체의 중앙으로 이동하는 과정과 OBB 모델로 그리퍼와 물체 정렬 후 집는 과정을 나누어서 실습을 진행합니다.

## 목차
- [Lecture 4: Pick and Place](#lecture-4-pick-and-place)
	- [목차](#목차)
	- [1. gripper 연습해보기](#1-gripper-연습해보기)
		- [1.1 그리퍼를 여닫는 스크립트 (Day2 복습)](#11-그리퍼를-여닫는-스크립트-day2-복습)
	- [2. 물체 Detect 후 중앙 이동](#2-물체-detect-후-중앙-이동)
	- [3. OBB 모델로 그리퍼와 물체 정렬 및 집기](#3-obb-모델로-그리퍼와-물체-정렬-및-집기)
		- [3.1 OBB 모델로 물체의 회전각과 중심의 3D 좌표를 전송하는 파이썬](#31-obb-모델로-물체의-회전각과-중심의-3d-좌표를-전송하는-파이썬)
		- [3.2 그리퍼의 `pose`를 받아와서 Pick and Place 작동하는 스크립트](#32-그리퍼의-pose를-받아와서-pick-and-place-작동하는-스크립트)
	- [4. 시연 영상](#4-시연-영상)
	- [5. 마무리](#5-마무리)


## 1. gripper 연습해보기
본 강의에서는 **OnRobot RG2-FT**(URCap 5.10.1) 그리퍼를 사용합니다. 그리퍼를 여닫는 방법은 Day2 [Lecture 2](../../Session2_gripper_urcaps/lecture2/README.md)에서 배운 것과 같습니다.

> 참고 링크: [Onrobot urp 다운로드 링크](https://df.onrobot.com/)

> 그리퍼 연습은 Day2의 [`answer/gripper_open_close.script`](../../Session2_gripper_urcaps/answer/gripper_open_close.script)를 사용합니다.

### 1.1 그리퍼를 여닫는 스크립트 (Day2 복습)
#### 예제코드(Day2 gripper_open_close.script 본문):
```python
  rg2ft_grip(100.0, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)    # 열기 (폭 100mm)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
  sleep(1.0)
  rg2ft_grip(20.0, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)     # 닫기 (폭 20mm)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
```
URCaps로 만든 스크립트는 본문 앞에 **그리퍼 설정과 함수 정의**(`# begin: URCap Installation Node` ~ `# end: URCap Installation Node`)가 매우 깁니다. 이 부분이 있어야 본문에서 `rg2ft_grip(...)`을 부를 수 있으므로 지우지 않습니다.

1. `rg2ft_grip(width, force, tool_index, blocking, depth_comp, popupmsg)`
손가락 사이를 `width`(mm)만큼 벌리거나 좁힘. `force`(N)는 잡는 힘.  
   - `blocking=True`면 동작이 끝날 때까지 대기  
2. `rg2ft_payload_set(mass, tool_index, use_guard)`
물체 무게를 로봇에 알려주는 줄. 이번 실습에서는 무게를 0으로 둠.  

## 2. 물체 Detect 후 중앙 이동
여러 물체 중 원하는 물체의 중심 위로 로봇을 보내는 과정입니다. Day4 4단계 [`practice/4_yolo_move.py`](../../Session4_visionAI_yolo/practice/4_yolo_move.py)와 같은 동작이라 여기서는 다시 다루지 않습니다.

> 원본 예제 `2_pose_init.py`(초기 위치로 이동)와 `3_move_to_obj_center.py`(Detection 모델로 물체 중심 위로 이동)는 이 폴더에 그대로 있습니다.

## 3. OBB 모델로 그리퍼와 물체 정렬 및 집기
원하는 물체의 중심 위로 이동한 후 OBB 모델을 사용하여 물체의 회전각을 구합니다. 물체의 중심 3D 좌표와 회전각을 함께 전달하여 그리퍼의 `pose`를 전달합니다. 로봇은 `pose`를 받아와서 이동한 후 그리퍼를 이용하여 물체를 잡고 지정된 위치에 가져다 놓습니다.

### 3.1 OBB 모델로 물체의 회전각과 중심의 3D 좌표를 전송하는 파이썬
#### 예제코드(4_pickup_obb.py):
`4_pickup_obb.py`를 실행시킵니다. 실행시, 그리퍼에 부착되어있는 3D 카메라로 현재 판 위에 존재하는 물체를 캡쳐합니다. 이후, 사전 학습된 YOLO OBB 모델을 불러오고, 캡쳐한 이미지 내에 존재하는 물체를 탐지합니다.

```Python
box = box_dict[cls_id]
print(box['xywhr'])
if box['xywhr'][2] < box['xywhr'][3]:
	angle = box['xywhr'][4]
else:
	angle = box['xywhr'][4] - np.pi/2

cx=box['xyxy'][0] + box['xyxy'][2]
cy=box['xyxy'][1] + box['xyxy'][3]
cx = int(cx/2)
cy = int(cy/2)

# 3D 위치 계산
intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
pos_3d = get_3d_position(cx, cy, depth_frame, intrinsics)
```

obb 모델의 결과값은 Detection 모델과 유사하나, 추가적으로 `xywhr` 속성이 포함되어 있으며, 이는 바운딩 박스의 회전각 `r`을 포함합니다. 해당 각도를 이용하여 UR 로봇의 손목에 `r`만큼 회전하도록 명령을 내림으로서 물체와 그리퍼를 정렬시킬 수 있습니다. 회전각과 물체의 중심좌표를 `handle_client()`에서 로봇으로 전달합니다.

### 3.2 그리퍼의 `pose`를 받아와서 Pick and Place 작동하는 스크립트
#### 예제코드(pickup.script):
> 아래 코드는 원본 장비(OnRobot 2FG7) 기준입니다. RG2-FT에서는 `twofg_grip`/`twofg_release` 대신 `rg2ft_grip(폭, 힘, ...)`을 씁니다. RG2-FT로 집고 놓는 전체 흐름은 아래 실습 3을 참고합니다.

```python
    #######################
    # request pose_add data
    #######################
    socket_send_line("req_data", "socket_0")
    sleep(0.1)
    buf = socket_read_ascii_float(6, socket_name = "socket_0", timeout = 2)
    p_tot = p[buf[1], buf[2], buf[3], 0.0, 0.0, buf[6]]

    textmsg("tool flange: ", get_actual_tool_flange_pose())
    set_tcp(tcp_camera)
    p_ = get_actual_tcp_pose()
    textmsg("p_: ", p_)
    tool_pose = pose_trans(p_, p_tot)
    textmsg("tool_pose: ", tool_pose)
    set_tcp(tcp_gripper)

    
    ###################
    # pick and place
    ###################

    # move to object
    set_tcp(tcp_gripper)
    movel(tool_pose, a = 1.2, v = 0.05, t = 0, r = 0.0)

    #hold
    on_return = twofg_grip(width = 33.0, force = 50, speed = 100, external_grip = True, tool_index = 0)
    textmsg("hold")

    #move to initial position
    set_tcp(p[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    p_init_ = [1.57, -1.57, 1.57, -1.57, -1.57, 0.0]  # [rad]
    movej(p_init_, a = 1.2, v = 0.3, t = 0, r = 0)

    p_end_ = [0, -1.57, 1.57, -1.57, -1.57, 0.0]  # [rad]
    movej(p_end_, a = 1.2, v = 0.3, t = 0, r = 0)
    
    set_tcp(tcp_gripper)
    p_ = get_actual_tcp_pose()
    p_final_ = p[p_[0], p_[1], 0.10, p_[3], p_[4], p_[5]]
    movel(p_final_, a = 1.2, v = 0.1, t = 0, r = 0)

    on_return = twofg_release(width = 70.0, speed = 100, external_release = True, tool_index = 0)
    textmsg("release")

    set_tcp(p[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    movej(p_end_, a = 1.2, v = 0.3, t = 0, r = 0)
    movej(p_init_, a = 1.2, v = 0.3, t = 0, r = 0)
```
물체의 카메라 기준 상대 pose를 받아 절대 목표 pose(`tool_pose`)를 계산한 뒤, 그리퍼 TCP를 기준으로 접근·집기, 플랜지/그리퍼 TCP를 전환하여 이동·배치·복귀까지 수행하는 Pick&Place 시퀀스입니다.

#### 동작 순서
1. **좌표 수신 (카메라 기준 상대 pose)**
   - `socket_send_line("req_data", "socket_0")`로 외부에 pose 데이터 요청
   - `socket_read_ascii_float(6, ...)`로 6개의 float 데이터 수신 (`buf`)
   - `p_tot = p[buf[1], buf[2], buf[3], 0.0, 0.0, buf[6]]`  
     → X, Y, Z, RZ 정보를 활용해 **카메라 TCP 기준 상대 pose** 구성

2. **절대 목표 pose 계산**
   - `set_tcp(tcp_camera)`로 **카메라 TCP 활성화**
   - `p_ = get_actual_tcp_pose()`로 카메라 TCP의 **절대 pose** 취득
   - `tool_pose = pose_trans(p_, p_tot)`  
     → 절대 목표 pose = (카메라 TCP 절대 pose) + (카메라 기준 상대 pose)

3. **Pick (접근 및 파지)**
   - `set_tcp(tcp_gripper)`로 **그리퍼 TCP 활성화**
   - `movel(tool_pose, a=1.2, v=0.05, ...)`  
     → 그리퍼 TCP 기준 직선 접근
   - `twofg_grip(width=33.0, force=50, speed=100, ...)`  
     → 지정 간격·힘·속도로 파지

4. **중간 자세 복귀 (플랜지 기준 이동)**
   - `set_tcp(p[0,0,0,0,0,0])`로 **TCP 오프셋 초기화** (플랜지 기준)
   - `movej(p_init_, ...)` → 안전 초기 자세로 이동
   - `movej(p_end_, ...)` → 배치 지점 방향의 중간 자세로 이동

5. **Place (하강, 배치, 해제)**
   - `set_tcp(tcp_gripper)`로 **그리퍼 TCP 활성화**
   - `p_ = get_actual_tcp_pose()` 현재 그리퍼 TCP 절대 pose
   - `p_final_ = p[p_[0], p_[1], 0.10, p_[3], p_[4], p_[5]]`  
     → XY/자세 유지, Z=0.10m로 설정
   - `movel(p_final_, a=1.2, v=0.1, ...)` → 안전 높이까지 하강
   - `twofg_release(width=70.0, speed=100, ...)` → 파지 해제

6. **정리 복귀**
   - `set_tcp(p[0,0,0,0,0,0])` (플랜지 기준)
   - `movej(p_end_)` → `movej(p_init_)` 순으로 복귀

---

#### 핵심 포인트
- **좌표계 전환(`set_tcp`)**:  
  - 계산 단계 → `tcp_camera`  
  - 접근·집기·배치 → `tcp_gripper`  
  - 전이·복귀 → 플랜지 기준 (`p[0...0]`)
- **`pose_trans`의 역할**:  
  카메라 TCP 절대 pose와 카메라 기준 상대 pose를 합성해 베이스 좌표계 기준 절대 pose를 생성
- **이동 명령 선택**:  
  - `movej`: 관절 공간 이동(빠른 전환, 안전 경로)  
  - `movel`: TCP 직선 경로(정밀 접근/배치)
- **안전 높이 확보**:  
  배치 시 Z=0.10m처럼 여유 높이를 설정해 충돌을 방지

> 실습: [`practice/1_pick_place.py`](../practice/1_pick_place.py) — 찾은 물체를 집어서 놓을 곳에 내려놓기 (정답: [`answer/1_pick_place.py`](../answer/1_pick_place.py))

> 실습: [`practice/2_obb_output.py`](../practice/2_obb_output.py) — OBB 출력 보기 (정답: [`answer/2_obb_output.py`](../answer/2_obb_output.py))

> 실습: [`practice/3_straighten_angle.py`](../practice/3_straighten_angle.py) — 얼마나 돌리면 똑바로 서는지 구하기 (정답: [`answer/3_straighten_angle.py`](../answer/3_straighten_angle.py))

> 실습: [`practice/4_straighten_pick.py`](../practice/4_straighten_pick.py) — 삐뚤어진 물체를 집어서 놓을 곳에 똑바로 내려놓기 (정답: [`answer/4_straighten_pick.py`](../answer/4_straighten_pick.py))

## 4. 시연 영상
<p align="center">
  <a href="https://youtu.be/Q2dVi6PPn1A">
    <img src="https://img.youtube.com/vi/Q2dVi6PPn1A/maxresdefault.jpg" alt="시연 영상" width="80%">
  </a>
  <p align="center">
  ▲ 이미지를 클릭하면 YouTube에서 영상을 볼 수 있습니다.
</p>


## 5. 마무리
이번 실습을 통해 YOLO 기반 물체 인식, 3D 좌표 추출, TCP 좌표계 변환, 그리고 OnRobot RG2-FT 그리퍼를 활용한 Pick & Place 작업의 전체 과정을 구현해 보았습니다. 카메라와 그리퍼의 TCP를 적절히 전환하며 좌표 변환(`pose_trans`)을 수행하는 방법과, `movej`/`movel` 명령의 선택 기준을 실습으로 익혔습니다. 이 과정을 바탕으로 다양한 환경에서의 물체 정렬, 배치, 조립 등의 작업으로 확장할 수 있습니다.