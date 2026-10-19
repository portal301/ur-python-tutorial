# Lecture 1: Pick and Place - 데이터셋 수집 
로봇이 사물을 인식하기 위해 YOLO와 같은 비전AI 를 이용합니다. 그러나 우리가 실습에서 사용하는 물건이나, 실무에서 사용하게 될 물건들은 기존의 YOLO를 학습시키기 위한 데이터셋에 포함이 되어있지 않을 가능성이 높습니다. 따라서 우리는 감지 대상이 될 물체에 대한 **커스텀 데이터셋**을 만들어야 합니다.  

커스텀 데이터셋을 만드는 방법에는 여러 가지가 있습니다. 직접 핸드폰으로 사진을 찍을 수도 있고 아니면 로봇이 직접 카메라를 이용하여 데이터를 수집할 수 있습니다. 본 강의에서는 **realsense** 카메라를 이용하여 **로봇이 바닥에 놓여진 물체 주위를 회전하면서 다각도로 물체의 사진을 저장하는 방법**을 학습합니다.

## 목차
- [Lecture 1: Pick and Place - 데이터셋 수집](#lecture-1-pick-and-place---데이터셋-수집)
  - [목차](#목차)
  - [1. 초기 위치 설정](#1-초기-위치-설정)
    - [1.1 초기 위치를 전송하는 파이썬](#11-초기-위치를-전송하는-파이썬)
    - [1.2 초기 위치로 이동하는 스크립트](#12-초기-위치로-이동하는-스크립트)
    - [1.3 생각해보기](#13-생각해보기)
  - [2. 로봇이 돌아가면서 물체의 사진 찍기](#2-로봇이-돌아가면서-물체의-사진-찍기)
    - [2.1 통신 흐름 정하기](#21-통신-흐름-정하기)
    - [2.2 육각형의 꼭짓점 `pose` 계산하기](#22-육각형의-꼭짓점-pose-계산하기)
  - [2.3 realsense를 이용하여 이미지 저장하기](#23-realsense를-이용하여-이미지-저장하기)
  - [2.4 로봇의 `pose`전송 및 이미지 촬영을 처리하는 클라이언트 함수](#24-로봇의-pose전송-및-이미지-촬영을-처리하는-클라이언트-함수)
    - [2.5 `pose`를 받아오고 이동 완료 신호를 보내는 스크립트](#25-pose를-받아오고-이동-완료-신호를-보내는-스크립트)
    - [2.6 실행결과](#26-실행결과)
    - [2.7 더 해보기](#27-더-해보기)
    - [2.8 추가 질문](#28-추가-질문)
  - [3. 마무리](#3-마무리)



## 1. 초기 위치 설정
`1_init_pose.py`를 실행하여 로봇을 초기 위치로 이동합니다.

### 1.1 초기 위치를 전송하는 파이썬
#### 예제코드(1_init_pose.py):
```python
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8').rstrip()  # Remove trailing newline

            print(f"Received from {addr}: {message}")

            if message == "initialize":
                print("Received initialization request")
                p_init = [90.000/180*pi, -90.000/180*pi, 90.000/180*pi, -90.000/180*pi, -90.000/180*pi, 0.000] # 로봇의 초기 joint state
                float_string = "({})\n".format(','.join(map(str, p_init)))
                writer.write(float_string.encode())
                await writer.drain()

    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()
```
로봇의 `joint parameter`를 전송하는 클라이언트입니다. p_init에 90도를 라디안 단위로 변환하여 리스트로 저장한 후 인코딩하여 로봇에 전송합니다. 

### 1.2 초기 위치로 이동하는 스크립트
#### 예제코드(init_pose.script):
```python
def init_pose():
    server_ip = "192.168.1.7"
    port = 12345

    socket_open(server_ip,port,"socket_0")

    socket_send_line("initialize","socket_0")
    sleep(0.1)

    buf=socket_read_ascii_float(6,socket_name="socket_0", timeout=2)

    p_init = [buf[1],buf[2],buf[3],buf[4],buf[5],buf[6]]

    movej(p_init, a=1.2, v=0.3, t=0, r=0)
    
    socket_close("socket_0")
    sleep(0.1)
end
```
`init_pose.script`에서는 서버(노트북)과의 통신을 위한 소켓을 연 후 `"initialize"`문자열을 전송합니다. 그 후 버퍼에 들어오느 `joint parameter`를 읽어와서 movej에 넣어줍니다. `Day3/3_robot_remoting`의 `7_set_position2.py`를 통해 `joint parameter`로 로봇을 이동하는 방법을 다시 확인할 수 있습니다. 마지막으로 소켓을 닫으면서 통신을 마무리합니다. 

### 1.3 생각해보기
- 이번 스크립트에서는 왜 `trans_pos()`함수를 사용하지 않았을까요?
- `movej()`에 `pose`와 `joint parameter`가 둘 다 들어갈 수 있을까요?
  - Hint: References의 URscript manual에서 함수의 상세정보를 검색해보세요.


## 2. 로봇이 돌아가면서 물체의 사진 찍기
### 2.1 통신 흐름 정하기
본 과정에서는 로봇이 바닥에 놓인 물체 주위의 6개의 점에서 realsense를 이용하여 물체의 이미지를 저장하려고 합니다. 이 과정에서 필요한 부분들을 생각해보면 다음과 같습니다. 

> 1. 초기 위치를 중심으로 한 육각형의 각 꼭짓점의 `pose` 계산
> 2. 로봇이 각 꼭짓점에 도달했을 시 realsense로 **이미지 저장**

위 두 가지의 과정을 통신 흐름을 고려하여 구체화 하면 다음과 같이 흐름을 구성할 수 있습니다. 

> 1. 서버(노트북)에서 육각형의 꼭짓점 `pose` 계산(위치가 이동해도 카메라는 물체를 바라보도록 **회전각 계산**)
> 2. 계산한 `pose`를 소켓을 통해 로봇으로 전달
> 3. 로봇에서 `pose`를 받아와서 이동
> 4. 로봇에서 이동 완료 후 완료했다는 신호를 다시 서버(노트북)로 전달
> 5. 이동 완료 신호를 받은 서버(노트북)에서 realsense로 이미지 저장
> 6. 이미지 저장 완료 후 다음 `pose`를 로봇으로 전달

이제 각 과정을 코드로 구현해봅시다.

### 2.2 육각형의 꼭짓점 `pose` 계산하기
#### 예제코드(2_collect_data.py):
```python
def generate_circle_poses(radius, num_points=6):
    poses = []
    for i in range(num_points):
        poses.append(get_relative_pose(radius, i, num_points))
    poses.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # 마지막에 원점으로 돌아오기
    return poses
```
`generate_circle_poses()` 함수는 로봇이 물체를 촬영하기 위해 이동할 **pose 목록**을 생성합니다.   

이 함수는 `get_relative_pose()` 함수(뒤에서 설명)를 사용하여 지정한 반지름(`radius`)과 점 개수(`num_points`)에 맞춰 원 위의 위치를 계산하고, 각 위치에서 로봇이 물체 중심을 바라보도록 회전값을 함께 포함합니다. 계산된 pose들은 리스트에 순서대로 저장되며, 마지막에는 원점 복귀 pose를 추가하여 촬영이 끝난 뒤 로봇이 처음 위치로 돌아올 수 있도록 합니다. 모든 pose 값은 `1_init_pose.py`로 설정한 초기 위치를 기준으로 한 **상대 좌표**입니다.

꼭짓점의 pose를 직접 계산하는 `get_relative_pose()`함수의 구조는 다음과 같습니다. 

```python
def get_relative_pose(radius, index, num_points=6):
    theta = 2 * pi * index / num_points
    
    # dx, dy, dz 계산 
    dx = radius * cos(theta)
    dy = radius * sin(theta)
    dz = 0.0

    # rx, ry, rz 계산
    # 1. 벡터 정규화
    v = np.array([dx, dy, 0.5 - dz]) 
    norm = np.linalg.norm(v)
    vx, vy, vz = v / norm

    # 2. 기준 z축 벡터
    z_axis = np.array([0, 0, 1])
    target_dir = np.array([vx, vy, vz])

    # 3. 외적과 내적 계산
    axis = np.cross(z_axis, target_dir)
    dot_product = np.dot(z_axis, target_dir)

    # 4. 각도 계산 (acos의 인자가 -1~1 범위 넘어가지 않도록 clip)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))

    # 5. 회전 벡터 (axis * angle)
    if np.linalg.norm(axis) == 0:
        rx, ry, rz = 0.0, 0.0, 0.0
    else:
        axis = axis / np.linalg.norm(axis)
        rx, ry, rz = - axis * angle

    return [dx, dy, dz, rx, ry, rz]
```
`get_relative_pose()` 함수는 초기 위치를 기준으로 한 **상대 pose**를 계산하여 반환합니다.  
지정한 반지름(`radius`)과 점의 인덱스(`index`), 총 점 개수(`num_points`)를 이용해 원 위의 좌표 `(dx, dy, dz)`를 구하고, 해당 위치에서 로봇이 물체 중심을 바라보도록 회전값 `(rx, ry, rz)`를 함께 계산합니다.  

1. **위치 계산 (`dx, dy, dz`)**  
   - 원주 각도 `theta`를 계산하고, 반지름에 따라 `dx`와 `dy`를 구합니다.  
   - 높이 변화(`dz`)는 0으로 설정됩니다.
2. **회전 계산 (`rx, ry, rz`)**  
   - 목표 방향 벡터를 만들고(`v`), 이를 정규화하여 단위 벡터로 변환합니다.  
   - 기준 z축 벡터와의 외적, 내적을 이용해 회전 축(`axis`)과 회전 각도(`angle`)를 계산합니다.  
   - 회전 벡터는 `axis * angle` 형태로 구하며, 로봇이 항상 물체 중심을 향하도록 합니다.
3. **반환값**  
   - `[dx, dy, dz, rx, ry, rz]` 형태의 리스트를 반환하며, 이는 `generate_circle_poses()`에서 사용됩니다.


## 2.3 realsense를 이용하여 이미지 저장하기
각 꼭짓점에 도달했을 때 realsense를 이용하여 이미지를 촬영 및 저장하는 부분입니다.

#### 예제코드(2_collect_data.py):
```python
def capture_image(pipeline, filename="output.jpg"):

    save_dir = "img"
    os.makedirs(save_dir, exist_ok=True)  # ./img 폴더가 없으면 생성

    # Flush old frames (RealSense가 최신 프레임을 제공하도록 몇 장 버림)
    for _ in range(5):
        pipeline.wait_for_frames()
    
    # Capture the frame
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    if not color_frame:
        print("[ERROR] No color frame captured.")
        return False

    # Convert to numpy array
    color_image = np.asanyarray(color_frame.get_data())

    # Save the image
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, color_image)
    print(f"[INFO] Image saved to: {filename}")
    return True
```

`capture_image()` 함수는 **Intel RealSense 카메라**를 이용해 이미지를 촬영하고 지정한 파일 이름으로 저장합니다.  
촬영 전 불필요한 이전 프레임을 제거하여 최신 영상을 저장하도록 하며, 저장 위치는 기본적으로 `./img` 폴더입니다.

1. **저장 폴더 생성**  
   - `img` 폴더가 없으면 `os.makedirs()`로 새로 생성합니다.
2. **프레임 버리기 (Flush)**  
   - `pipeline.wait_for_frames()`를 5회 호출하여 카메라 버퍼에 남아있는 오래된 프레임을 제거하고, 최신 상태의 프레임만 사용합니다.
3. **이미지 캡처**  
   - 새 프레임을 받아(`frames`), 컬러 프레임(`color_frame`)만 추출합니다.  
   - 컬러 프레임이 없으면 오류 메시지를 출력하고 `False`를 반환합니다.
4. **데이터 변환**  
   - RealSense 프레임 데이터를 NumPy 배열(`color_image`)로 변환합니다.
5. **이미지 저장**  
   - 지정한 파일명(`filename`)으로 `img` 폴더에 저장합니다.  
   - 저장 성공 시 파일 경로를 출력하고 `True`를 반환합니다.

## 2.4 로봇의 `pose`전송 및 이미지 촬영을 처리하는 클라이언트 함수
서버와 로봇이 연결되었을 때 실행되는 클라이언트입니다. `main()`함수에서 초기에 1회 실행됩니다. 

#### 예제코드(2_collect_data.py):
```python
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8').rstrip()  # Remove trailing newline
            print(f"Received from {addr}: {message}")

            if message == "req_data":
                print("Received data request")

                poses = generate_circle_poses(0.15) # 0.15m radius
                for pose in poses:
                    print2(f"Sending pose: {pose}", Color.GREEN)
                    float_string = "({})\n".format(','.join(map(str, pose)))
                    writer.write(float_string.encode())
                    await writer.drain()
                    await asyncio.sleep(0.1)  # 다음 포즈 보내기 전 대기
                    
                    # "reached"가 도착하면 이미지 캡쳐
                    data = await reader.read(1024)
                    message = data.decode('utf-8').rstrip()
                    if message == "reached":
                        capture_image(pipeline, f"pose_{poses.index(pose)}.jpg")
                    
    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        print(f"Connection with {addr} reset")
    finally:
        print(f"Connection with {addr} closed")
        writer.close()
```

`handle_client()` 함수는 로봇과의 **TCP 통신**을 처리하며, 로봇의 위치 이동과 RealSense 카메라 촬영을 제어합니다.  
로봇으로부터 데이터 요청을 받으면 촬영 경로에 해당하는 pose를 순차적으로 전송하고, 각 위치에 도달했을 때 이미지를 촬영합니다.

1. **클라이언트 연결 수락**  
   - `reader`와 `writer`를 통해 로봇과 TCP 연결을 수립하고, 연결된 클라이언트의 주소를 출력합니다.
2. **메시지 수신 및 처리**  
   - 로봇으로부터 수신한 메시지를 UTF-8로 디코딩하고, 문자열 끝의 개행 문자를 제거합니다.
   - `"req_data"` 메시지를 받으면 데이터 전송 프로세스를 시작합니다.
3. **촬영 경로 pose 전송**  
   - `generate_circle_poses(0.15)`를 호출하여 반지름 0.15m의 원 위 pose 목록을 생성합니다.
   - 각 pose를 문자열로 변환 후 로봇에 전송(`writer.write()`), 전송 버퍼를 비움(`await writer.drain()`).
   - pose 전송 간 0.1초 대기하여 로봇이 명령을 순차적으로 처리할 수 있도록 함.
4. **이미지 촬영 트리거**  
   - pose 전송 후 로봇으로부터 `"reached"` 메시지가 오면, 해당 pose 인덱스에 맞춰 이미지를 촬영(`capture_image()`).
   - 촬영된 이미지는 `pose_0.jpg`, `pose_1.jpg` 등의 파일명으로 저장됨.
5. **연결 종료 처리**  
   - 예외(`CancelledError`, `ConnectionResetError`)를 처리한 뒤 연결을 종료하고 리소스를 정리합니다.


### 2.5 `pose`를 받아오고 이동 완료 신호를 보내는 스크립트
로봇은 서버(노트북)에서 전송한 로봇의 상대 `pose`를 받아와서 `절대 pose`(로봇의 base frame을 기준으로 한 `pose`)를 계산하고 이동한 후, 이동 완료 신호를 보내고 다음 `pose`를 기다리는 동작을 합니다.

```python
i = 0
while i < 7:
    buf = socket_read_ascii_float(6, socket_name="socket_0", timeout = 0)
    p_rel = p[buf[1], buf[2], buf[3], buf[4], buf[5], buf[6]]
    p_target = pose_trans(p_init, p_rel)

    textmsg("Moving to:", p_target)
    movej(p_target, a=1.2, v=0.1)

    socket_send_line("reached","socket_0")
    sleep(0.5)
    i = i + 1
end
```

위 URScript 코드는 로봇이 순차적으로 여러 pose로 이동하면서, 각 위치에 도달했을 때 **이동 완료 신호**를 PC로 전송하는 동작을 수행합니다. 주로 `handle_client()` 함수와 함께 사용되어 촬영 지점마다 카메라 트리거 역할을 합니다.

1. **반복 제어 (`while i < 7`)**  
   - 총 7개의 pose에 대해 이동을 수행합니다.  
   - 여기서 6개의 촬영 위치 + 마지막 원점 복귀 pose를 포함합니다.
2. **pose 데이터 수신**  
   - `socket_read_ascii_float(6, socket_name="socket_0", timeout=0)`을 통해 PC에서 전송한 pose 데이터를 읽어옵니다.  
   - `timeout=0`으로 설정하면 **버퍼에 데이터가 들어올 때까지 대기**하며, 데이터가 준비되면 즉시 읽어옵니다.  
   - `buf[1]`~`buf[6]` 값은 각각 `dx, dy, dz, rx, ry, rz`에 해당합니다.
3. **목표 pose 계산**  
   - `p_rel` : 상대 pose  
   - `p_target = pose_trans(p_init, p_rel)` : 초기 pose(`p_init`)를 기준으로 상대 pose를 적용한 절대 pose를 계산합니다.
4. **로봇 이동**  
   - `movej(p_target, a=1.2, v=0.1)`을 사용하여 해당 pose로 조인트 이동을 수행합니다.
5. **이동 완료 신호 전송**  
   - 이동이 끝나면 `"reached"` 메시지를 소켓을 통해 PC로 전송하여, 카메라 촬영을 트리거합니다.
6. **대기 및 인덱스 증가**  
   - `sleep(0.5)`로 잠시 대기한 뒤, `i`를 증가시켜 다음 pose로 넘어갑니다.

### 2.6 실행결과
각 위치에서 찍은 사진이 img 폴더에 저장되는 것을 확인할 수 있습니다.

### 2.7 더 해보기
- 로봇이 물체 주위로 8등분한 점에서 사진을 찍으려면 코드를 어떻게 수정하면 될까요?

### 2.8 추가 질문
- 로봇의 위치가 이동해도 카메라가 물체를 바라보게끔 하기 위해서 `get_relative_pose()`에서 `rx, ry, rz`를 어떻게 계산한 걸까요? 오일러 회전각을 바탕으로 찾아보세요.


## 3. 마무리
이번 실습을 통해 로봇에 realSense 카메라를 장착하여 **커스텀 데이터셋**을 수집하는 전 과정을 경험했습니다. 초기 위치 설정부터, 원 위의 여러 지점으로 로봇을 이동시키며 물체를 다양한 각도에서 촬영하는 방법을 익혔습니다.

이러한 데이터 수집 방식은 실제 산업 현장이나 연구 프로젝트에서 YOLO와 같은 비전 AI 모델을 **특정 환경과 대상에 최적화**하는 데 유용하게 활용될 수 있습니다. 향후에는 다양한 배경·조명·거리 조건에서 촬영을 시도하여 모델의 **일반화 성능**을 더욱 높일 수 있습니다.
