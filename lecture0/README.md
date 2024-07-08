# Lecture 0: 파이썬 빠르게 살펴보기

이 트레이닝 세션은 파이썬을 잘 몰라도 전반적인 흐름을 이해할 수 있도록 답안이 제공되고 있습니다. 파이썬을 잘 모른다면 아래의 문법/기능 정도만 이해하면 진행이 수월할 거예요.

우선 터미널 프롬프트에서 아래 명령어를 통해 lecture0 폴더로 이동하겠습니다. (해당 위치를 프로그램 실행/참조의 기준위치로 설정함)

    cd lecture0

## 1. 이 정도만 알면 간단한 해석은 될거예요.

### 리스트 (List)
리스트는 여러 개의 항목을 하나의 변수에 저장할 수 있는 데이터 타입입니다. 항목들은 순서가 있으며, 인덱스를 통해 접근할 수 있습니다.

#### 예시:
```python
# 리스트 생성
fruits = ["apple", "banana", "cherry"]

# 항목 접근
print(fruits[0])  # apple

# 리스트에 항목 추가
fruits.append("orange")

# 리스트 항목 제거
fruits.remove("banana")

# 리스트 길이 확인
print(len(fruits))  # 3
```

### 딕셔너리 (Dictionary)
딕셔너리는 키-값 쌍을 저장하는 데이터 타입입니다. 각 키는 고유하며, 이를 통해 값에 접근할 수 있습니다.

#### 예시:
```python
# 딕셔너리 생성
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# 값 접근
print(person["name"])  # John

# 값 변경
person["age"] = 31

# 키-값 쌍 추가
person["job"] = "Engineer"

# 키-값 쌍 제거
del person["city"]

# 딕셔너리 길이 확인
print(len(person))  # 3
```

### 조건문 (if)
조건문은 주어진 조건이 참인지 거짓인지에 따라 다른 코드를 실행할 수 있게 합니다.

#### 예시:
```python
x = 10
y = 20

if x > y:
    print("x는 y보다 큽니다.")
elif x < y:
    print("x는 y보다 작습니다.")
else:
    print("x와 y는 같습니다.")
```
### 반복문 (while/for)
반복문은 특정 조건이 참인 동안 또는 주어진 시퀀스의 각 항목에 대해 코드를 반복 실행합니다.

#### while 문 예시:
```python
count = 0

while count < 5:
    print(count)
    count += 1
```
### for 문 예시:
```python
코드 복사
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
```

### 함수 (Function)
함수는 재사용 가능한 코드 블록으로, 특정 작업을 수행하기 위해 호출될 수 있습니다.

```python
# 함수 정의
def greet(name):
    return f"Hello, {name}!"

# 함수 호출
print(greet("Alice"))  # Hello, Alice!

# 인자가 없는 함수
def say_hello():
    print("Hello!")

say_hello()  # Hello!
```


## 2. class를 알면 프로그램을 예쁘게 정리할 수 있어요.

프로그램 재생산성을 향상하기 위해서는 작업한 코드를 class로 묶어서 컴포넌트화하는게 중요해요.

트레이닝 세션에서는 간단한 코드위주로 class를 비중있게 다루진 않기 때문에 이런게 있구나 정도만 알면 돼요.


## 3. 시스템 최적화

로봇과 주변기기들 간의 통신 시스템을 구축할 때, 각 기기의 독립적인 동작 과정에서 비동기성이 발생할 수 있습니다. 이를 처리하기 위해 비동기 프로그래밍을 적용하고, 발생할 수 있는 다양한 오류를 예외처리로 다루며, 프로세스 병목현상을 줄이기 위해 큐(queue)를 사용할 수 있습니다.

### 비동기 프로그래밍 (asyncio)
Python의 asyncio 모듈을 사용하면 비동기 I/O 작업을 효율적으로 처리할 수 있습니다. 이는 특히 소켓 통신과 같은 I/O 바운드 작업에 유용합니다.

```python
import asyncio

async def handle_robot(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    print(f"Received: {message}")

    response = "Message received"
    writer.write(response.encode())
    await writer.drain()

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_robot, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

### 예외처리 (try/except/else/finally)
비동기 프로그래밍에서는 다양한 오류가 발생할 수 있으므로, 이를 적절히 처리하여 시스템의 안정성을 유지하는 것이 중요합니다.

```python
import asyncio

async def risky_operation():
    try:
        # 위험한 작업 수행
        result = 1 / 0
    except ZeroDivisionError as e:
        print(f"Error occurred: {e}")
    else:
        print("Operation succeeded")
    finally:
        print("Cleaning up resources")

asyncio.run(risky_operation())
```

### 큐 (queue)
큐를 사용하면 여러 프로세스 간의 작업을 효율적으로 관리할 수 있습니다. 비동기 큐를 사용하여 작업 간 병목 현상을 줄일 수 있습니다.

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await asyncio.sleep(1)
        item = f"item {i}"
        await queue.put(item)
        print(f"Produced {item}")

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))
    
    await producer_task
    await queue.put(None)  # 소비자에게 작업 종료를 알림
    await consumer_task

asyncio.run(main())
```
위의 예시에서는 비동기 프로그래밍을 통해 로봇과 컴퓨터 간의 통신을 처리하고, 발생할 수 있는 오류를 예외처리로 다루며, 큐를 사용하여 작업을 효율적으로 관리하는 방법을 보여줍니다. 이를 통해 독립적인 동작 과정에서 발생할 수 있는 비동기성과 오류를 효과적으로 처리할 수 있습니다.
