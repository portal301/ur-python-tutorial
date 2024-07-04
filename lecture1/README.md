# Lecture 1 TCP 소켓 통신에 대한 이해
## 강의 목표
TCP 소켓 서버와 클라이언트 프로그램을 실행해보면서, TCP 통신 시스템에 대한 이해를 얻습니다.

## TCP란
**TCP**는 Transmission Control Protocol의 줄임말로서, 컴퓨터가 네트워크상의 다른 기기와 통신하기 위한 통신규약입니다.
각각의 패킷(통신 단위) 전송에 일종의 송장번호인 SYN와 ACK값을 함께 전송하면서 패킷이 유실되는 상황을 인식하고, 재전송 할 수 있어 안정적인 통신 방식입니다.
### SYN, ACK
![image](https://github.com/portal301/ur-python-tutorial/assets/5483768/b2b69ba6-9b46-4ebf-b89d-f0ee765f2649)

TCP 통신에서는 각 패킷의 헤더에 SYN과 ACK 값을 포함하여, 패킷의 순서와 해당 패킷에 대한 응답을 추적할 수 있습니다. 이를 통해 TCP는 실패한 패킷을 자동으로 감지하고, 재전송할 수 있습니다.


## 실습
### #1
#### 코드 실행
command prompt를 두개 열고, ```cd {프로젝트 경로 이름}``` 명령어를 통해 프로젝트가 설치된 디렉토리에 접속합니다.

***ex***
```bash
cd Document/Portal301/ur-python-tutorial/lecture1
```

**Bash**에 다음 명령어를 입력해봅니다.

```    
python lecture1_server.py
```
```
python lecture1_client.py
```

#### 코드 분석 : Client.py
```python
import socket

def start_client(host='127.0.0.1', port=65432, message="Hello, Server!"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port)) # 127.0.0.1:65432 소켓에 접속
        s.sendall(message.encode()) # String 형식의 message를 Byte 형식으로 인코딩
        data = s.recv(1024) # 127.0.0.1:65432에서 메시지가 전송되기까지 기다림
        print(f"Received from server: {data.decode()}") # Server로 부터 전송받은 메시지를 byte에서 String으로 변환

if __name__ == "__main__":
    start_client()
```
#### 코드 설명
1. 프로그램이 실행되면, ```s.connect()``` 함수를 사용해서 default 값으로 지정해둔 host, port값을 통해 소켓에 접속 시도합니다.
    - 실무에서는 접속의 실패를 감안해서, ```try-catch``` 구문으로 예외처리를 실행해야 합니다.
2. 소켓에 접속이 성공하면 ```encode()```함수로 ```message``` 변수를 ***byte*** 형식으로 디코딩 후 ```sendall()``` 함수를 통해 전송합니다.
3. ```recv()``` 함수는 연결된 소켓으로부터 메시지를 받는 함수입니다. 
   - 매개변수의 ***1024***는 총 1024바이트를 저장하겠다는 의미입니다. 따라서 2000바이트가 들어오든, 4000바이트가 들어오든 1024바이트만 끊어서 저장하게됩니다.
   - 메시지가 오지 않는다면 올때가지 기다리게 됩니다.
   - 따라서 이후 ```print```문은 만약 메시지가 전송되지 않으면 실행되지 않습니다.   

#### 코드 분석 : Server.py
```Python
import socket

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # 소켓 생성
        s.bind((host, port)) #127.0.0.1:65432 IP와 포트로 소켓을 생성할 준비
        s.listen() # 소켓을 수신 대기 상태로 설정합니다
        print(f"Server listening on {host}:{port}")
        
        conn, addr = s.accept() # 클라이언트의 연결 요청을 수락합니다
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024) # 1024 바이트의 메시지를 전송받습니다.
                if not data: 
                    break 
                print(f"Received: {data.decode()}") 
                conn.sendall(data)  # 전송받은 메시지를 소켓 연결된 대상에게 다시 전송합니다.

if __name__ == "__main__":
    start_server()
```

#### 코드 설명
1. 프로그램이 실행되면, ```socket.socket()``` 함수를 통해 소켓을 생성합니다.
2. ```bind()``` 함수를 통해 default 값으로 지정해둔 host, port값을 소켓에 바인딩합니다. 이는 차후 다른 프로그램이 해당 포트를 점유하려 할때 운영체제가 이를 방지할 수 있습니다.
3. 소켓에 접속이 성공하면 ```encode()```함수로 ```message``` 변수를 ***byte*** 형식으로 디코딩 후 ```sendall()``` 함수를 통해 전송합니다.
4. ```recv()``` 함수는 연결된 소켓으로부터 메시지를 받는 함수입니다. 
   - 매개변수의 ***1024***는 총 1024바이트를 저장하겠다는 의미입니다. 따라서 2000바이트가 들어오든, 4000바이트가 들어오든 1024바이트만 끊어서 저장하게됩니다.
   - 메시지가 오지 않는다면 올때가지 기다리게 됩니다.
   - 따라서 이후 ```print```문은 만약 메시지가 전송되지 않으면 실행되지 않습니다.   


- server_forever를 실행해봅니다.


    python lecture1_server_forever.py

    python lecture1_client.py --> N회 실행

    (실행 완료 후 서버 쪽 프롬프트는 강제 종료)


- 비동기 서버를 실행해봅니다.


    python lecture1_server_forever_async.py

    python lecture1_client.py --> N회 실행

    (서버 쪽 프롬프트는 control+c 단축키를 이용하여 종료)


* 위 세가지 방법에는 어떤 차이가 있었을지 분석해볼까요?
