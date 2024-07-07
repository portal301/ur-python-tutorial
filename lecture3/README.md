# Lecture 3

## 실습목표

지난 강의(Lecture 2)에서는 로봇에 스크립트를 전송하여 명령을 전달하는 과정을 배웠습니다. 이번 강의에서는 로봇으로부터 데이터를 수신하고, 이를 통해 실제로 로봇을 움직이는 방법을 다루겠습니다.

이를 통해 우리는 로봇의 현재 상태를 모니터링하고, 실시간으로 제어하는 기술을 익히게 될 것입니다. 각 단계별로 데이터를 어떻게 수집하고, 이를 기반으로 로봇의 동작을 어떻게 제어할 수 있는지 구체적으로 살펴보겠습니다.

이 강의를 통해 로봇과의 양방향 통신 및 제어에 대한 이해를 더욱 깊이 있게 발전시킬 수 있을 것입니다.


## 로봇의 소켓 열기

컴퓨터에서 로봇으로 스크립트 파일을 전송할 때는, 로봇에서 미리 열어둔 30001 또는 30002 포트를 사용했습니다.

반대로 로봇에서 컴퓨터로 데이터를 전송하려면, 컴퓨터에서 특정 포트(이번 코드에서는 12345번)를 미리 열어두어야 합니다.

그 후, 로봇의 30001번 포트를 사용하여 컴퓨터의 소켓에 접속하는 클라이언트 코드를 주입하면 됩니다.

코드 전문은 hellosocket.py 파일에서 확인할 수 있습니다.

### hellosocket.py
```python
async def main(host='127.0.0.1', port=12345):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")
    print("Sending script to the robot...")

    await asyncio.sleep(0.1)
    sendScriptFile(robot_ip, script_path, PORT_PRIMARY_CLIENT)

    async with server:
        await server.serve_forever()
```

`hellosocket.py`의 `main` 함수에서는 비동기 방식으로 socket을 열고, 소켓이 열린 뒤 0.1초뒤에 스크립트 파일을 로봇으로 전송합니다.

스크립트 파일의 코드는 다음과 같습니다.

### hellosocket.script
```python
def hellosocket():
    server_ip = "192.168.0.2"
    port=12345
    socket_open(server_ip,port,"socket_0")
    socket_send_line("hello socket from robot","socket_0")
    socket_close("socket_0")
end
```
UR 로봇에서는 ***urp*** 프로그래밍 언어를 사용합니다. 이 언어는 파이썬에서 소켓을 사용하는 방식과 매우 유사합니다.

- socket_open() 함수를 사용하여 소켓을 엽니다.
- socket_send_line() 함수를 통해 원하는 데이터를 소켓으로 전송합니다.
- socket_close() 함수를 사용하여 소켓을 닫습니다.

로봇의 현재 위치 값을 이러한 방식으로 얻어보겠습니다. 자세한 내용은 [여기](https://github.com/portal301/ur-python-tutorial/blob/main/scriptManual_SW5.11.pdf)에서 확인할 수 있습니다.

## Pose와 Joint Parameter
UR 로봇을 제어할 때, pose와 joint 파라미터는 서로 다른 방식으로 로봇의 위치와 자세를 정의합니다.

### Pose
로봇의 TCP(툴 센터 포인트)의 위치와 방향을 나타내는 파라미터입니다. 이는 일반적으로 6개의 요소로 구성되며, 첫 세 가지는 X, Y, Z 좌표를 나타내고 나머지 세 가지는 롤(roll), 피치(pitch), 요(yaw) 각도를 나타냅니다. pose 파라미터를 사용하면 로봇의 TCP가 공간에서 특정 위치와 방향을 취하도록 설정할 수 있습니다. 이는 주로 작업의 끝점을 정의하거나 특정 궤적을 따라 이동할 때 사용됩니다.

### Joint Parameter 
로봇의 각 관절의 각도를 나타내는 파라미터입니다. UR 로봇은 일반적으로 6축 로봇이므로, joint 파라미터는 6개의 각도로 구성됩니다. 각 값은 각 관절의 회전 각도를 의미합니다. joint 파라미터를 사용하면 로봇의 각 관절을 개별적으로 제어할 수 있어, 특정 작업 공간 내에서 로봇의 자세를 세밀하게 조정할 수 있습니다. 이는 주로 로봇의 초기 설정이나 정밀한 동작이 필요할 때 사용됩니다.



## 로봇의 현재 정보 보내기 - Pose

이번 실습에서는 로봇의 현재 정보를 보내는 방법에 대해 알아보겠습니다.

코드 전문은 `get_position1.py`와 `get_position1.script`에 존재합니다.
### get_position1.script
```python
def socket_get_position1():
    server_ip = "192.168.0.2"
    port = 12345
    socket_open(server_ip,port,"socket_0")

    socket_send_line("current_pos","socket_0")
    sleep(0.1)

    p_=get_actual_tcp_pose()

    i=0
    while (i<6):
        socket_send_int(p_[i]*10000)
        i=i+1
    end

    socket_close("socket_0")
end
```

해당 함수는 컴퓨터에서 열어둔 포트에 접속하여. 현재 pose값을 전송합니다. `get_actual_tcp_pose()` 함수는 현재 로봇의 pose 값, 즉 `X,Y,Z,RX,RY,RZ` 정보를 배열로 반환합니다. 

이때 코드를 보시면, `p[i]`를 한자리(digit)씩 보내는 것을 알 수 있습니다.

## 로봇의 현재 정보 받아오기 - Pose
이렇게 한자리씩 보낸 배열값을 한번에 파싱하려면 어떻게 해야할까요?

해당 코드는 `get_position1.py` 파일의 `handle_pos_data()` 함수에 구현되어있습니다.

```python
async def handle_pos_data(reader):
    integers_data = []
    # Receive 24 bytes (6 integers = 6 * 4 bytes = 24 bytes) 
    data = await reader.readexactly(24)
    # Unpack the 6 short integers from the received data
    print("position data:", data)
    integers_data = struct.unpack('>iiiiii', data)
    actual_pos_data = [x/10000 for x in integers_data]

    return actual_pos_data
```
여기서 우리는 다음 라인에 주목해야합니다.

`data = await reader.readexactly(24)` 

이 코드는 소켓에 전송된 payload값이 24바이트가 될때까지 기다리는 함수입니다.

`Int`는 4 bytes 이므로 즉, 총 6자리 배열을 받아오는 역할을 합니다.

이때 보낼 당시 `float`(소수) 형식의 데이터에 10000을 곱해 보냈기 때문에 다시 10000을 나눠서 원래 값과 동일하게 만들어 줍니다.

## 로봇의 현재 정보 보내기 - Joint Param
로봇의 현재 모습을 표현하는 방식에는 `X,Y,Z,RX,RY,RZ`를 표현하는 pose도 있지만, 각 6개의 관절값을 저장하고 있는 **joint parameter**도 존재합니다.

이를 보내는 방식은 다음과 같습니다. 코드 전문은 `get_position2.py`에 존재합니다.
```python
    q_=get_actual_joint_positions()
    i=0
    while (i<6):
        socket_send_int(q_[i]*10000)
        i=i+1
    end
```
pose 값을 보냈을때와 사실 코드의 큰 차이는 존재하지 않습니다. 단지 함수가 `get_actual_tcp_pose`에서 `get_actual_joint_positions()`로 바뀌었을 뿐입니다. 

pose와 마찬가지로 joint parameter도 6자리 배열값이므로, 소켓을 받아오는 방식은 동일합니다. 

## 로봇의 pose값으로 움직여보기 
로봇의 현재 정보를 받아보았으니, 이번엔 반대로 로봇을 움직이는 스크립트를 전송해보겠습니다.
코드 전문은 `set_position1.script`에 있습니다.

```python
    buf=socket_read_ascii_float(6,socket_name="socket_0", timeout=2)
    #p_rel = p[0,0,0.05,0,0,0]
    p_rel = p[buf[1],buf[2],buf[3],buf[4],buf[5],buf[6]]
    socket_close("socket_0")

    q_=get_actual_joint_positions()
    p_ready=get_forward_kin(q=q_,tcp=p_rel)

    movej(p_ready, a=1.2, v=0.1, t=0, r=0.0)
```
```buf=socket_read_ascii_float(6,socket_name="socket_0", timeout=2)``` 이 코드는 ```컴퓨터 -> 로봇```으로 전송된 6자리 배열을 파싱하는 함수입니다.

이때 주의할 점은 실제 배열은 7자리이며, 첫 `buf[0]`은 전송된 배열 `payload`의 크기 즉 6을 담고있습니다.

`get_actual_joint_positions()` 함수를 통해 현재 **joint parameter**값을 `q_`에 저장합니다.

이후 `get_forward_kin()` 함수를 사용하여 현재의 관절값 `q_`에서 `p_rel`만큼 이동한 값을 계산합니다.

이후 `movej()` 함수를 통해 로봇을 이동할 수 있습니다.

## 로봇의 joint parameter값 전송하기
로봇을 이동하는 방식은 pose 값을 전송하는 방식도 있지만, joint paramter값을 전송해서 할 수 있습니다.

우리는 다음 스크립트를 통해서 엔드이팩터가 `p_goal`에 도착하기 이전에, `q_ready`를 사용해 로봇에게 특정 동작을 지시한 하려고 합니다.

코드의 전문은 `set_position.script`에 존재합니다

```python
    buf=socket_read_ascii_float(18,socket_name="socket_0", timeout=2)
    p_goal = p[buf[1],buf[2],buf[3],buf[4],buf[5],buf[6]]
    p_rel = p[buf[7],buf[8],buf[9],buf[10],buf[11],buf[12]]
    q_ref = [buf[13],buf[14],buf[15],buf[16],buf[17],buf[18]]

    ...

    p_=get_actual_tcp_pose()
    q_=get_actual_joint_positions()

    q_goal = get_inverse_kin(p_goal,q_ref)
    p_ready = get_forward_kin(q=q_goal,tcp=p_rel)
    q_ready = get_inverse_kin(p_ready,q_ref)

    movej(q_ref, a=1.2, v=0.1, t=0, r=0)
    sleep(1)
    movej(q_ready, a=1.2, v=0.1, t=0, r=0.01)
    movel(q_goal, a=1.2, v=0.1, t=0, r=0)
```

각 변수들은 다음 역할을 담당합니다.
```python
p_goal = p[buf[1], buf[2], buf[3], buf[4], buf[5], buf[6]]
p_rel = p[buf[7], buf[8], buf[9], buf[10], buf[11], buf[12]]
q_ref = [buf[13], buf[14], buf[15], buf[16], buf[17], buf[18]]
```

1. `p_goal`은 목표 위치를 나타내며, buf의 `1`번부터 `6`번 요소를 사용합니다.
2. `p_rel`은 상대 위치를 나타내며, buf의 `7`번부터 `12`번 요소를 사용합니다.
3. `q_ref`는 기준 관절 위치를 나타내며, buf의 `13`번부터 `18`번 요소를 사용합니다.
   
```python
p_ = get_actual_tcp_pose()
q_ = get_actual_joint_positions()
```

1. p_는 현재 TCP(툴 센터 포인트)의 위치를 가져옵니다.
2. q_는 현재 관절 위치를 가져옵니다.

```python
q_goal = get_inverse_kin(p_goal, q_ref)
p_ready = get_forward_kin(q=q_goal, tcp=p_rel)
q_ready = get_inverse_kin(p_ready, q_ref)
```
1. `q_goal`은 `p_goal` 위치에서의 역기구학(inverse kinematics)을 계산하여 관절 위치를 구합니다.
2. `p_ready`는 `q_goal` 관절 위치에서의 순기구학(forward kinematics)을 계산하여 `p_rel` TCP 위치를 구합니다.
3. `q_ready`는 `p_ready` 위치에서의 역기구학을 계산하여 관절 위치를 구합니다.


```python
movej(q_ref, a=1.2, v=0.1, t=0, r=0)
sleep(1)
movej(q_ready, a=1.2, v=0.1, t=0, r=0.01)
movel(q_goal, a=1.2, v=0.1, t=0, r=0)
```

1. `movej(q_ref, a=1.2, v=0.1, t=0, r=0)`은 로봇을 `q_ref` 조인트 파라미터 값을 사용하여 로봇을 움직입니다. 가속도는 1.2, 속도는 0.1입니다.
2. `sleep(1)`은 1초 동안 대기합니다.
3. `movej(q_ready, a=1.2, v=0.1, t=0, r=0.01)`은 로봇을 `q_ready` 조인트 파라미터 값을 사용하여 로봇을 움직입니다. 가속도는 1.2, 속도는 0.1이며, 도달 반경은 0.01입니다.
4. `movel(q_goal, a=1.2, v=0.1, t=0, r=0)`은 로봇을 `q_goal` 위치로 선형 이동시킵니다. 가속도는 1.2, 속도는 0.1입니다.

