# Universal Robots Quick Tutorial - External Control with Python

### Introduction

파이썬을 이용하여 유니버셜로봇을 외부 컴퓨터로 제어하는 방법을 학습하기 위한 프로젝트 페이지입니다.

유니버설 로봇 지정 트레이닝센터에서 오프라인 트레이닝 세션이 정기적으로 진행되며, 트레이닝센터의 로봇 시스템 구성은 아래와 같습니다.


- 파이썬 python version: 3.11.x 

- 로봇 모델 Robot model: UR3e

- 로봇 소프트웨어 버전 Polyscope version: 5.11~5.12

- 주변기기: URCaps Grippers(Robotiq two-finger gripper 등), IO제어 컨베이어벨트, IO 포토(위치)센서

- 네트워크: 로컬 네트워크 라우터 사용


위의 구성이 아니더라도 튜토리얼을 진행하는데는 크게 무리가 없을 것으로 생각합니다.

혹시 문제가 발생하거나 추가 요청사항이 있을경우 Issue탭이나 contact@portal301.com으로 문의주세요 :)



### 프로젝트 다운받기

1. ZIP file

'<>Code' button -> Download ZIP


2. git clone (git bash 필요)

프로젝트 폴더 만든후 해당 폴더에서 터미널 실행 -> 터미널 프롬프트에서 아래 명령 입력

    git clone git@github.com:portal301/ur-python-tutorial.git



### 개발환경

1. VScode 설치

https://code.visualstudio.com/download


2. python 설치

- 다운로드 페이지: https://www.python.org/downloads/

3.11.x 버전을 권장합니다.

- VScode에서 python extension을 설치하세요.



- (optional) python venv (virtual environment)

파이썬 프로젝트를 동시에 여러가지 진행할 경우 라이브러리 충돌이 발생할 수 있습니다. 가상환경은 라이브러리 저장공간을 분리하여 라이브러리 간의 충돌을 방지합니다.

수업에서 직접 다루지는 않지만, 배워두면 유용합니다.


3. (optional) git bash

- 다운로드 페이지: https://git-scm.com/

Github과의 호환성이 좋은 터미널 프로그램입니다.



4. github copilot

- 소개 페이지: https://code.visualstudio.com/docs/copilot/overview

AI를 이용하여 개발속도를 극적으로 향상시킬 수 있습니다. 다만 기본이 부족한 상태에서 AI에 의존하게 되면 어느순간 벽을 만나게 될 수 있으니 지혜롭게 활용해보아요.


Written by AffineRobotics(Portal301)