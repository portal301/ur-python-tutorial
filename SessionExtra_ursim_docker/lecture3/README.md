# Lecture 3
## 강의 목표
- Day 1에서 만든 코드를 IP만 바꿔서 가상 로봇에 연결합니다.
- 로봇 → PC 접속이 컨테이너에서는 어떻게 달라지는지 이해합니다.

## 실습전에
Lecture 2처럼 URSim을 실행하고, PolyScope에서 로봇을 **정상(Normal)** 상태로 켜 둡니다.

## 실습 1: 스크립트 보내기 (Day 1 Lecture 2)
Lecture 2의 실행 명령에서 포트(`-p`)를 내 PC로 연결했기 때문에, 로봇 IP를 **`127.0.0.1`** (내 PC 자신)로 바꾸면 됩니다.

`Session1_ur_external_control/lecture2/helloworld.py`
```python
robot_url = "127.0.0.1"
```
실행 후 PolyScope 화면에 `Happy learning!` 창이 뜨면 성공입니다.

`scriptfile.py` 도 같은 방법으로 `robot_url` 만 바꿔서 `slowmove.script` 등을 보내 봅니다.

## 실습 2: 로봇이 PC에 접속하기 (Day 1 Lecture 3)
Lecture 3은 **로봇이 PC 서버에 접속**하는 구조라서 IP를 세 군데 바꿔야 합니다.

| 위치 | 원래 값 | 바꿀 값 |
|---|---|---|
| 파이썬 `robot_ip` | 로봇 IP | `"127.0.0.1"` |
| 파이썬 `server_ip` (서버를 여는 주소) | PC IP | `"0.0.0.0"` |
| `.script` 안의 `server_ip` (로봇이 접속할 주소) | PC IP | 지금 내 PC의 이더넷/와이파이 IP (`ipconfig` 로 확인) |

- 컨테이너 안에서 `127.0.0.1` 은 내 PC가 아니라 **컨테이너 자신**입니다. 그래서 로봇 쪽 스크립트에는 내 PC의 실제 IP를 넣어야 합니다.
- `0.0.0.0` 은 "내 PC의 모든 네트워크에서 접속을 받겠다"는 뜻입니다.

순서대로 `hellosocket.py` → `get_position1.py` → `set_position1.py` 를 실행해 봅니다.
- `get_position1.py` 는 PolyScope **이동** 탭에서 로봇을 움직인 뒤 다시 실행하면 값이 바뀌는지 확인합니다.
