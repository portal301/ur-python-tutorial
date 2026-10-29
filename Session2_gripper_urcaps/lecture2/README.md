# Lecture 2: 저장한 위치로 Pick and Place

## 강의 목표
- Lecture 1의 그리퍼 열기/닫기에 **로봇 이동**을 더해 물체를 집고 놓는 흐름을 이해합니다.
- Day 1에서 배운 위치 받기로 집을 곳/놓을 곳 좌표를 확인하고, 완성된 코드에 넣어 실행해봅니다.

- 예제: [`scripts/pick_and_place.script`](./scripts/pick_and_place.script) (좌표는 예시값이므로 그대로 쓰지 마세요)


## 1. 코드 살펴보기

스크립트 앞부분(1 ~ 3128줄)은 Lecture 1의 `gripper_open_close.script`와 같습니다. 그리퍼 설정과 `rg2ft_grip()` 정의가 들어 있으므로 지우지 않습니다. 본문은 3129줄부터입니다.

### 1.1 좌표
```python
  pick_pose = p[0.0, -0.40, 0.10, 0.0, 3.14, 0.0]      # 집을 곳
  place_pose = p[0.20, -0.40, 0.10, 0.0, 3.14, 0.0]    # 놓을 곳
  up = p[0, 0, 0.10, 0, 0, 0]                          # 10cm 위
```
- `p[x, y, z, rx, ry, rz]`: 베이스 기준 자세(m, rad)입니다.
- `pose_add(pose, up)`: `pose`에서 z만 10cm 높인 자세입니다. 물체에 바로 내려가지 않고 위에서 수직으로 접근하기 위해 씁니다.

### 1.2 동작 순서
```
열기 → 집을 곳 10cm 위 → 내려가기 → 닫기 → 올라가기
     → 놓을 곳 10cm 위 → 내려가기 → 열기 → 올라가기
```
```python
  movel(pose_add(pick_pose, up), a=0.5, v=0.1)         # 집을 곳 10cm 위
  movel(pick_pose, a=0.5, v=0.05)                      # 내려가기
  rg2ft_grip(20.0, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)   # 닫기
```
- 이동은 `movel`(직선 이동), 그리퍼는 Lecture 1의 `rg2ft_grip(...)` 그대로입니다.
- 내려가고 올라올 때는 속도를 `v=0.05`(5cm/s)로 느리게 합니다.
- `blocking=True`라서 그리퍼가 다 닫힌 뒤에 다음 이동을 시작합니다.


## 2. 실습: 내 좌표로 Pick and Place

### 2.1 좌표 확인하기
Day 1 Lecture 3의 [로봇의 현재 정보 받아오기 - Pose](../../Session1_ur_external_control/lecture3/README.md#로봇의-현재-정보-받아오기---pose)를 이용합니다.
1. 펜던트로 로봇을 움직여 그리퍼가 물체를 **잡을 수 있는 위치**에 둡니다.
2. 위치 받기를 실행해 `[x, y, z, rx, ry, rz]`를 기록합니다. → **집을 곳**
3. 같은 방법으로 **놓을 곳** 좌표도 기록합니다.

### 2.2 실행하기
1. `scripts/pick_and_place.script`의 `pick_pose`, `place_pose`를 기록한 좌표로 바꿉니다.
2. `gripper.py`에서 로봇 IP를 확인합니다.
```python
robot_url = "192.168.1.104"
script_path = "scripts/pick_and_place.script"
```
3. 펜던트를 **원격제어(Remote) 모드**로 두고, `lecture2` 폴더에서 실행합니다. 이상하면 바로 펜던트 비상정지 버튼을 누르세요.
```bash
cd Session2_gripper_urcaps/lecture2
python gripper.py
```

#### 실행 결과
- 로봇이 집을 곳에서 물체를 집어 놓을 곳에 내려놓습니다.

### 더 해보기
- 놓을 곳을 하나 더 정해서, 물체를 두 번 옮겨보세요.
- 물체 크기에 맞게 닫는 폭(`20.0`)과 힘(`40.0`)을 바꿔보세요.


## 3. 마무리

이번 실습에서는 그리퍼 열기/닫기에 로봇 이동을 더해 물체를 집고 놓아 보았습니다.

지금은 좌표를 직접 넣었기 때문에 물체가 조금만 옮겨져도 집지 못합니다. 다음 날부터는 카메라로 물체의 위치를 직접 찾아보겠습니다. Day 5에서는 이 흐름에서 `pick_pose` 자리만 카메라가 찾은 좌표로 바뀝니다.
