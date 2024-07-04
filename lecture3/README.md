# Lecture 3

## 실습목표

지난 Lecture2에는 로봇에 스크립트를 전송해 명령을 전달하는 과정에 대해 알아보았습니다. 

이번 강의에서는 로봇으로부터 데이터를 받아오고, 실제로 로봇을 움직여보는 방식에 대해 알아보겠습니다.

## 로봇의 소켓 열기

컴퓨터에서 로봇에 스크립트 파일을 전송할때는, 로봇에 미리 열려있던 `30001` 혹은 `30002`포트에 전송했습니다.

반대로 로봇에서 컴퓨터에 전송하기 위해서 

컴퓨터에 미리 포트를 열어두고, 로봇의 30001번 포트로 컴퓨터 소켓에 접속하는 클라이언트 코드를 주입하면 됩니다.

코드 전문은 `hellosocket.py`에서 확인하시기 바랍니다.

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
스크립트는 UR 로봇에 사용되는 urp라는 프로그래밍 언어입니다.

그러나 전체적인 구조는 파이썬에서 소켓을 사용할 때와 매우 비슷합니다.

`socket_open()` 함수를 통해 소켓을 열고, `socket_send_line()` 함수를 통해 원하는 데이터를 해당 소켓을 통해 전송합니다. 그리고 `socket_close()` 함수로 소켓을 닫습니다.

해당 언어에 대한 자세한 문서는 [여기](https://github.com/portal301/ur-python-tutorial/blob/main/scriptManual_SW5.11.pdf)에서 확인하실 수 있습니다.

이러한 방식으로 로봇의 현재 위치값을 얻어보겠습니다.

## 로봇의 현재 정보 가져오기

