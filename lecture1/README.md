# Lecture 0 & 1
## Lecture 0: 파이썬 빠르게 살펴보기

이 트레이닝 세션은 파이썬을 잘 몰라도 전반적인 흐름을 이해할 수 있도록 답안이 제공되고 있습니다. 파이썬을 잘 모른다면 아래의 문법/기능 정도만 이해하면 진행이 수월할 거예요.


### 1. 이 정도만 알면 간단한 해석은 될거예요.

list, dictionary, while/for/if, function


### 2. class를 알면 프로그램을 예쁘게 정리할 수 있어요.

프로그램 재생산성을 향상하기 위해서는 작업한 코드를 class로 묶어서 컴포넌트화하는게 중요해요.

트레이닝 세션에서는 간단한 코드위주로 class를 비중있게 다루진 않기 때문에 이런게 있구나 정도만 알면 돼요.


### 3. 시스템 최적화

비동기프로그래밍(asyncio), 예외처리(try/except/else/finally), 큐(queue)

로봇과 주변기기들 간의 통신 시스템을 구축할 경우 각 기기의 독립적인 동작과정에서 비동기성이 발생할 수 있습니다.

여기서 이런저런 오류가 발생하거나, 프로세스 병목현상이 발생할 수 있기 때문에 이를 처리하기 위한 다양한 기법이 필요할 수 있습니다.

트레이닝 세션에서는 컴퓨터와 로봇간의 소켓통신에 비동기 프로그래밍을 적용하여 연습해볼 거예요.


### Lecture 1: 

- command prompt를 두개 열고 서버(1회성)와 클라이언트를 하나씩 실행해봅니다.

    
    python lecture1_server.py

    python lecture1_client.py


- server_forever를 실행해봅니다.


    python lecture1_server_forever.py

    python lecture1_client.py --> N회 실행

    (실행 완료 후 서버 쪽 프롬프트는 강제 종료)


- 비동기 서버를 실행해봅니다.


    python lecture1_server_forever_async.py

    python lecture1_client.py --> N회 실행

    (서버 쪽 프롬프트는 control+c 단축키를 이용하여 종료)


* 위 세가지 방법에는 어떤 차이가 있었을지 분석해볼까요?