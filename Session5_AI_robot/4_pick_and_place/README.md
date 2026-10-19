# Lecture 4: Pick and Place

본 강의에서는 훈련시킨 YOLO 모델과 그리퍼를 이용하여 직접 `Pick and Place`를 구현해봅니다. 넓은 범위에서 물체를 감지하고 원하는 물체의 중앙으로 이동하는 과정과 OBB 모델로 그리퍼와 물체 정렬 후 집는 과정을 나누어서 실습을 진행합니다.

## 목차
- [Lecture 4: Pick and Place](#lecture-4-pick-and-place)
	- [목차](#목차)
	- [1. gripper 연습해보기](#1-gripper-연습해보기)
		- [1.1 gripper 스크립트를 전송하는 파이썬](#11-gripper-스크립트를-전송하는-파이썬)
		- [1.2 gripper를 작동시키는 스크립트](#12-gripper를-작동시키는-스크립트)
	- [2. 물체 Detect 후 중앙 이동](#2-물체-detect-후-중앙-이동)
		- [2.1 YOLO로 물체 인식 후 물체의 3D 좌표를 보내는 파이썬](#21-yolo로-물체-인식-후-물체의-3d-좌표를-보내는-파이썬)
		- [2.2 선택된 물체 중심의 3D 좌표를 이용하여 로봇을 이동시키는 스크립트](#22-선택된-물체-중심의-3d-좌표를-이용하여-로봇을-이동시키는-스크립트)
	- [3. OBB 모델로 그리퍼와 물체 정렬 및 집기](#3-obb-모델로-그리퍼와-물체-정렬-및-집기)
		- [3.1 OBB 모델로 물체의 회전각과 중심의 3D 좌표를 전송하는 파이썬](#31-obb-모델로-물체의-회전각과-중심의-3d-좌표를-전송하는-파이썬)
		- [3.2 그리퍼의 `pose`를 받아와서 Pick and Place 작동하는 스크립트](#32-그리퍼의-pose를-받아와서-pick-and-place-작동하는-스크립트)
	- [4. 시연 영상](#4-시연-영상)
	- [4. 마무리](#4-마무리)


## 1. gripper 연습해보기
본 강의에서는 **OnRobot의 2FG7** 모델을 사용합니다. 새로운 그리퍼를 사용할 때는 URCaps를 이용하여 예시 프로그램을 작성하고 스크립트를 받아와 분석할 수 있습니다. Onrobot을 위한 URCaps가 설치되어 있다면 활용하고, 아니라면 아래 링크를 참고하여 설치합니다.

> 참고 영상: [YouTube - 2FG7 세팅 영상](https://www.youtube.com/watch?v=OU_1vsGAWz4)  
> 참고 링크: [Onrobot urp 다운로드 링크](https://df.onrobot.com/)

### 1.1 gripper 스크립트를 전송하는 파이썬
#### 예제코드(1_grippper_example.py):
```python
script_path = "scripts/gripper_example.script"

async def main(host='0.0.0.0', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")
    print("Sending script to the robot...")

    await asyncio.sleep(0.1)
    sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

    async with server:
        await server.serve_forever()
```
본 코드에서는 서버의 역할이 크게 중요하지 않습니다. 단순하게 `gripper_example.script`를 로봇에세 보내는 역할만을 수행합니다.

### 1.2 gripper를 작동시키는 스크립트
#### 예제코드(gripper_example.script):
```python
  cnt = 0
  while (cnt < 2):
    on_return = twofg_grip(width = 33.0, force = 50, speed = 100, external_grip = True, tool_index = 0)
    twofg_payload_set(mass = 0.0, tool_index = 0, use_guard = True)

    on_return = twofg_release(width = 70.0, speed = 100, external_release = True, tool_index = 0)
    twofg_payload_set(mass = 0.0, tool_index = 0, use_guard = False)

    cnt = cnt + 1
  end
```
URCaps를 이용하여 작성한 프로그램에서는 스크립트 처음 부분에 초기 설정 및 함수 정의 부분이 매우 깁니다. 스크립트의 마지막 `while`문 이전의 약 1970 줄이 모두 **그리퍼와 로봇의 통신, 그리퍼의 위치 및 힘 지정 등에 관한 초기 설정과 함수 정의**입니다.

본 스크립트는 `while`문을 이용하여 그리퍼를 닫았다가 여는 과정을 2번 반복합니다. 
1. `twofg_grip(width, force, speed, external_grip, tool_index, blocking)`
지정한 폭·힘·속도로 그리퍼를 닫아 물체를 잡음.  
   - `external_grip`으로 외부/내부 제어 방식을 선택  
   - `blocking=True`면 동작이 끝날 때까지 대기  
   - 실패 시 오류 팝업을 띄우고 동작을 중지  
2. `twofg_payload_set(mass, tool_index, use_guard)`
그리퍼가 물체를 감지하면 해당 질량과 무게중심(CoG)을 로봇 컨트롤러에 설정.  
   - `use_guard=True`면 Grip Guard(충돌 방지) 기능 활성화  
   - 물체가 없으면 질량을 0으로 설정하고 Guard를 비활성화  


## 2. 물체 Detect 후 중앙 이동
넓은 범위에서 여러 물체 중 입력한 물체의 중심 좌표쪽으로 이동하는 과정입니다. `2_pose_init.py`를 실행시켜 로봇을 초기 위치로 이동시킨 후에 진행합니다. 

### 2.1 YOLO로 물체 인식 후 물체의 3D 좌표를 보내는 파이썬
이후, `3_move_to_obj_center.py`를 실행시킵니다. 실행시, 그리퍼에 부착되어있는 3D 카메라로 현재 판 위에 존재하는 물체를 캡쳐합니다. 이후, 사전 학습된 YOLO Detection 불러오고, 캡쳐한 이미지 내에 존재하는 물체를 탐지합니다.

```python
# YOLO 탐지
results = model(source=color_image, verbose=False)
print("YOLO 탐지 완료")
results[0].show()
boxes = results[0].boxes
box_dict = {}
for box in boxes:
	cls_id = int(box.cls[0])
	print(box)
	if cls_id in box_dict:
		if box_dict[cls_id].conf < box.conf:
			box_dict[cls_id] = box
	else:
		box_dict[cls_id] = box
```
코드의 해당 부분은 YOLO 모델을 사용한 결과를 처리하는 부분입니다. model 함수의 리턴값은 YOLO 탐지결과를 포함하는 객체로 주어집니다. 해당 객체에는 `boxes` 속성이 포함되어있으며, 감지한 물체들의 바운딩 박스에 대한 정보를 담고 있습니다. 각 박스에 대한 정보는 ID(`cls`), 신뢰도(`conf`), 바운딩 박스 좌표(`xyxy`) 등이 있으며, 이를 활용하여 동일한 물체가 여러번 판별되었을 경우 가장 신뢰도가 높은 물체를 저장합니다.

```Python
box = box_dict[cls_id]
x1, y1, x2, y2 = map(int, box.xyxy[0])
cx = (x1+x2)//2
cy = (y1+y2)//2
print((x1, y1), (x2, y2))

# 3D 위치 계산
intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
pos_3d = get_3d_position(cx, cy, depth_frame, intrinsics)
```

터미널에 집고자 하는 물체를 입력하면, 그 물체의 바운딩 박스정보를 가져옵니다. 그리고 바운딩 박스의 2차원 픽셀상 중심을 구한뒤, 3D 카메라의 깊이 정보를 이용하여 3차원 좌표로 변환합니다. 변환한 3D 좌표를 `handleclient()`에서 로봇으로 전송합니다. 

### 2.2 선택된 물체 중심의 3D 좌표를 이용하여 로봇을 이동시키는 스크립트
```python
def move_to_obj_center():
    server_ip = "192.168.1.7"
    port = 12345
    socket_open(server_ip,port,"socket_0")

    tcp_camera = p[-0.03, -0.06, 0.03, 0.0, 0.0, 0.0]
    tcp_gripper = p[0.0, 0.0, 0.1456, 0.0, 0.0, 0.0]
    set_tcp(tcp_camera)
    set_tcp(tcp_gripper)

    socket_send_line("req_data","socket_0")
    sleep(0.1)

    buf = socket_read_ascii_float(6, socket_name = "socket_0", timeout = 2)
    p_rel = p[buf[1],buf[2],buf[3]/2,0.0,0.0,0.0]

    set_tcp(tcp_camera)
    p_ = get_actual_tcp_pose()
    tool_pose = pose_trans(p_, p_rel)
    movej(tool_pose, a=1.2, v=0.3, t=0, r=0.0)
    
    socket_close("socket_0")
    sleep(0.1)
end
```
물체의 3D 좌표를 받아 **로봇 TCP를 물체 중심 위로 이동**시키는 함수입니다. TCP 설정, 좌표 변환(`pose_trans`), 그리고 TCP 기준 이동(`movej`)의 과정을 포함합니다.

#### 동작 순서
1. **소켓 연결**
   - `socket_open(server_ip, port, "socket_0")`  
     외부 서버(여기서는 192.168.1.7:12345)와 통신을 시작.

2. **TCP 정의**
   - `tcp_camera`: 카메라 좌표계에서의 TCP 위치/자세  
   - `tcp_gripper`: 그리퍼 좌표계에서의 TCP 위치/자세  
   - `set_tcp(tcp_camera)`, `set_tcp(tcp_gripper)`를 통해 사용 장비에 맞는 TCP를 지정 가능.

3. **3D 좌표 요청 및 수신**
   - `socket_send_line("req_data", "socket_0")`로 좌표 데이터 요청  
   - `socket_read_ascii_float(6, ...)`로 6개의 float 데이터를 수신 (`buf`에 저장)

4. **상대 좌표 계산**
   - `p_rel = p[buf[1], buf[2], buf[3]/2, 0.0, 0.0, 0.0]`  
     → 물체의 3D 좌표 중 Z축은 절반만 사용하여 **물체 중심 위**로 이동할 높이를 계산.

5. **현재 TCP 위치 → 목표 위치 변환**
   - `set_tcp(tcp_camera)`로 카메라 TCP를 활성화  
   - `p_ = get_actual_tcp_pose()`로 현재 TCP pose를 읽음  
   - `tool_pose = pose_trans(p_, p_rel)`로 현재 위치에 상대 좌표(`p_rel`)를 더해 목표 pose를 생성.

6. **TCP 기준 이동**
   - `movej(tool_pose, a=1.2, v=0.3, t=0, r=0.0)`  
     → 활성화된 TCP를 기준으로 조인트 이동 수행.

7. **소켓 종료**
   - `socket_close("socket_0")`로 통신 종료.

#### 핵심 포인트
- **TCP 설정 중요성**: `movej`는 **활성화된 TCP 좌표계**를 기준으로 동작하므로, 카메라·그리퍼 등 목적에 맞는 TCP를 사전에 지정해야 함.
- **`pose_trans` 사용 목적**: 현재 TCP pose(`p_`)와 상대 pose(`p_rel`)를 합산하여, 절대 pose(`tool_pose`)를 계산.
- **Z축 절반 적용 이유**: 물체의 중심 **위쪽**에서 접근하도록 높이를 조정.


## 3. OBB 모델로 그리퍼와 물체 정렬 및 집기
원하는 물체의 중심 위로 이동한 후 OBB 모델을 사용하여 물체의 회전각을 구합니다. 물체의 중심 3D 좌표와 회전각을 함께 전달하여 그리퍼의 `pose`를 전달합니다. 로봇은 `pose`를 받아와서 이동한 후 그리퍼를 이용하여 물체를 잡고 지정된 위치에 가져다 놓습니다.

### 3.1 OBB 모델로 물체의 회전각과 중심의 3D 좌표를 전송하는 파이썬
#### 예제코드(4_pickup_obb.py):
`4_pickup_obb.py`를 실행시킵니다. 실행시, 그리퍼에 부착되어있는 3D 카메라로 현재 판 위에 존재하는 물체를 캡쳐합니다. 이후, 사전 학습된 YOLO Detection 불러오고, 캡쳐한 이미지 내에 존재하는 물체를 탐지합니다.

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

## 4. 시연 영상
<p align="center">
  <a href="https://youtu.be/Q2dVi6PPn1A">
    <img src="https://img.youtube.com/vi/Q2dVi6PPn1A/maxresdefault.jpg" alt="시연 영상" width="80%">
  </a>
  <p align="center">
  ▲ 이미지를 클릭하면 YouTube에서 영상을 볼 수 있습니다.
</p>



## 4. 마무리
이번 실습을 통해 YOLO 기반 물체 인식, 3D 좌표 추출, TCP 좌표계 변환, 그리고 OnRobot 2FG7 그리퍼를 활용한 Pick & Place 작업의 전체 과정을 구현해 보았습니다. 카메라와 그리퍼의 TCP를 적절히 전환하며 좌표 변환(`pose_trans`)을 수행하는 방법과, `movej`/`movel` 명령의 선택 기준을 실습으로 익혔습니다. 이 과정을 바탕으로 다양한 환경에서의 물체 정렬, 배치, 조립 등의 작업으로 확장할 수 있습니다.