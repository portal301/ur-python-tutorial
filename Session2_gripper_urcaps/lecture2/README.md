# Lecture 2: 그리퍼 열기/닫기와 하드코딩 좌표로 집고 놓기

## 강의 목표
- Lecture 1에서 로봇으로부터 가져온 `.script` 파일에서 **그리퍼 열기/닫기에 필요한 부분만** 남겨봅니다.
- `rg2ft_grip()` 함수로 그리퍼를 원하는 폭만큼 열고 닫아봅니다.
- Day 1에서 배운 위치 받기로 좌표를 확인하고, 로봇 이동과 그리퍼를 묶어 **물체를 집고 놓아봅니다.**

> **TODO (강의장에서 확인할 것)**
> - 이 실습의 스크립트는 Lecture 1의 `example_urcaps_onrobot_rg2ft.script`(**OnRobot RG2-FT**, URCap 5.10.1)를 바탕으로 만들었습니다. 펜던트 실행은 확인했고, **PC에서 보내서 실행하는 것**은 아직 확인하지 못했습니다.
> - 실습 2에서 위치 받기로 읽은 좌표가 **그리퍼 끝(TCP) 기준**인지 확인해 주세요. 이 스크립트는 `set_tcp(...)`를 직접 쓰지 않고 URCap 안에서 TCP를 설정합니다.

## 목차
- [Lecture 2: 그리퍼 열기/닫기와 하드코딩 좌표로 집고 놓기](#lecture-2-그리퍼-열기닫기와-하드코딩-좌표로-집고-놓기)
  - [강의 목표](#강의-목표)
  - [목차](#목차)
  - [1. 가져온 스크립트 살펴보기](#1-가져온-스크립트-살펴보기)
  - [2. 필요한 부분만 남기기](#2-필요한-부분만-남기기)
  - [3. 실습 1: 그리퍼 열고 닫기](#3-실습-1-그리퍼-열고-닫기)
  - [4. 실습 2: 하드코딩 좌표로 집고 놓기](#4-실습-2-하드코딩-좌표로-집고-놓기)
  - [5. 마무리](#5-마무리)


## 1. 가져온 스크립트 살펴보기

Lecture 1의 `lecture1/scripts/example_urcaps_onrobot_rg2ft.script`는 펜던트에서 `RG2-FT Grip` 노드 2개(닫기, 열기)만 넣고 만든 프로그램입니다. 열어보면 크게 세 부분으로 나뉩니다.

| 줄 | 내용 | 남길까? |
|---|---|---|
| 1 ~ 57 | 로봇 기본 설정 (TCP, 입출력, 중력, 페이로드 등) | 남김 |
| 58 ~ 3130 | `# begin: URCap Installation Node` ~ `# end: URCap Installation Node`<br>그리퍼 설정과 **`rg2ft_grip()` 함수 정의** | 남김 |
| 3131 ~ | 본문: 반복문과 `rg2ft_grip(...)` 호출 | **필요한 것만** |

Installation Node 안에는 `rg2ft_grip()` 함수가 정의되어 있습니다.
```python
def rg2ft_grip(width,force,tool_index=0,blocking=True,depth_comp=False,popupmsg=True):
```
- `width`: 손가락 사이 폭(mm). 크면 열리고, 작으면 닫힙니다.
- `force`: 잡는 힘(N)

이 함수 정의가 없으면 본문에서 `rg2ft_grip(...)`를 부를 수 없으므로, **Installation Node는 지우지 않습니다.**


## 2. 필요한 부분만 남기기

원래 본문은 다음과 같습니다.
```python
  step_count_... = 0.0
  thread Step_Counter_Thread_...():
    ...
  end
  run Step_Counter_Thread_...()
  while (True):
    $ 2 "Robot Program"
    $ 3 "RG2-FT Grip"
on_return = rg2ft_grip(0.0, 40.0, tool_index = 0, blocking = True, depth_comp = False, popupmsg = True)
rg2ft_payload_set(mass = 0.0, tool_index = 0, use_guard = True)
    $ 4 "RG2-FT Grip"
on_return = rg2ft_grip(100.0, 3.0, tool_index = 0, blocking = True, depth_comp = False, popupmsg = True)
rg2ft_payload_set(mass = 0.0, tool_index = 0, use_guard = True)
  end
end
```
- `$ 2 "..."` 같은 줄은 펜던트 화면에 지금 실행 중인 노드를 표시하는 용도라 지워도 됩니다.
- `rg2ft_payload_set(...)`은 물체 무게를 로봇에 알려주는 줄입니다. 그리퍼 노드마다 자동으로 들어가며, 이번 실습에서는 무게를 0으로 둡니다.

스텝 카운터와 반복문(`while (True)`)을 지우고, 그리퍼 열기/닫기만 남기면 다음과 같습니다.
```python
  rg2ft_grip(100.0, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)    # 열기 (폭 100mm)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
  sleep(1.0)
  rg2ft_grip(20.0, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)     # 닫기 (폭 20mm)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
end
```
로봇 팔은 움직이지 않고 그리퍼만 열렸다 닫힙니다.


## 3. 실습 1: 그리퍼 열고 닫기

- 문제: [`practice/gripper_open_close.script`](../practice/gripper_open_close.script) (`# TODO` 2곳)
- 정답: [`answer/gripper_open_close.script`](../answer/gripper_open_close.script)

1. `practice/gripper_open_close.script` 맨 아래의 `____`를 채웁니다.
```python
  # TODO 1: 그리퍼 열기 (폭 100mm, 힘 40N)
  rg2ft_grip(____, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
  sleep(1.0)
  # TODO 2: 그리퍼 닫기 (폭 20mm, 힘 40N)
  rg2ft_grip(____, 40.0, tool_index=0, blocking=True, depth_comp=False, popupmsg=True)
  rg2ft_payload_set(mass=0.0, tool_index=0, use_guard=True)
```
2. `lecture2/gripper.py`에서 로봇 IP를 확인합니다.
```python
robot_url = "192.168.0.110"
script_path = "practice/gripper_open_close.script"
```
3. 펜던트를 **원격제어(Remote) 모드**로 두고 실행합니다.
```bash
cd Session2_gripper_urcaps
python lecture2/gripper.py
```

#### 실행 결과
- 그리퍼가 100mm로 열리고, 1초 뒤 20mm로 닫힙니다.

### 더 해보기
- 폭을 바꿔서 그리퍼가 조금만 열리게 해보세요.
- 힘(`force`)을 바꿔서 물체를 잡아보세요. 힘이 너무 크면 어떻게 될까요?


## 4. 실습 2: 하드코딩 좌표로 집고 놓기

- 문제: [`practice/pick_and_place.script`](../practice/pick_and_place.script) (`# TODO` 4곳)
- 정답: [`answer/pick_and_place.script`](../answer/pick_and_place.script) (좌표는 예시값이므로 그대로 쓰지 마세요)

### 4.1 좌표 확인하기
Day 1 Lecture 3의 [로봇의 현재 정보 받아오기 - Pose](../../Session1_ur_external_control/lecture3/README.md#로봇의-현재-정보-받아오기---pose)를 이용합니다.
1. 펜던트로 로봇을 움직여 그리퍼가 물체를 **잡을 수 있는 위치**에 둡니다.
2. 위치 받기를 실행해 `[x, y, z, rx, ry, rz]`를 기록합니다. → **집을 곳**
3. 같은 방법으로 **놓을 곳** 좌표도 기록합니다.

### 4.2 동작 순서
```
열기 → 집을 곳 10cm 위 → 내려가기 → 닫기 → 올라가기
     → 놓을 곳 10cm 위 → 내려가기 → 열기 → 올라가기
```
```python
  up = p[0, 0, 0.10, 0, 0, 0]                          # 10cm 위
  movel(pose_add(pick_pose, up), a=0.5, v=0.1)         # 집을 곳 10cm 위
```
- `pose_add(pose, up)`: `pose`에서 z만 10cm 높인 자세입니다. 물체에 바로 내려가지 않고 위에서 수직으로 접근하기 위해 씁니다.
- 내려가고 올라올 때는 속도를 `v=0.05`(5cm/s)로 느리게 합니다.

### 4.3 실행하기
1. `practice/pick_and_place.script`의 `____` 4곳을 채웁니다.
   - TODO 1, 2: 4.1에서 기록한 좌표
   - TODO 3, 4: 실습 1에서 쓴 `rg2ft_grip(...)` 닫기/열기
2. `lecture2/gripper.py`의 `script_path`를 바꿉니다.
```python
script_path = "practice/pick_and_place.script"
```
3. 펜던트를 **원격제어(Remote) 모드**로 두고 실행합니다. 이상하면 바로 펜던트 비상정지 버튼을 누르세요.
```bash
python lecture2/gripper.py
```

#### 실행 결과
- 로봇이 집을 곳에서 물체를 집어 놓을 곳에 내려놓습니다.


## 5. 마무리

이번 실습에서는 URCaps로 만든 긴 `.script`에서 그리퍼 열기/닫기에 필요한 부분만 남기고, 확인한 좌표로 물체를 집고 놓아 보았습니다.

지금은 좌표를 직접 넣었기 때문에 물체가 조금만 옮겨져도 집지 못합니다. 다음 날부터는 카메라로 물체의 위치를 직접 찾아보겠습니다.
