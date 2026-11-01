# Lecture 3
## 강의 목표
- Day 1에서 만든 코드를 IP만 바꿔서 가상 로봇에 연결합니다.
- 로봇 → PC 접속이 컨테이너에서는 어떻게 달라지는지 이해합니다.

## UR 포트 지도
UR 로봇은 네트워크로 여러 개의 "문(포트)"을 열어 둡니다. 문마다 주고받는 내용이 다릅니다.

| 포트 | 이름 | 하는 일 | 이 강의 |
|---|---|---|---|
| 29999 | 대시보드 | 텍스트 명령: 상태 묻기, 전원 켜기, 프로그램 불러오기/실행/정지 | `dashboard.py` |
| 30001 | Primary | 스크립트 받기 + 로봇 상태 보내기 (10Hz) | Day 1 |
| 30002 | Secondary | 스크립트 받기 + 로봇 상태 보내기 (10Hz) | `sync_once.py` |
| 30003 | Realtime | 스크립트 받기 + 관절·속도 등 상태 보내기 (500Hz) | `read_joints.py` |
| 30004 | RTDE | 원하는 데이터만 골라 주고받기 (전용 라이브러리 사용) | - |
| 502 | Modbus TCP | PLC 등 산업 장비와 레지스터로 주고받기 | - |

- 자세한 비교: [Overview of Client Interfaces](https://www.universal-robots.com/articles/ur/interface-communication/overview-of-client-interfaces/)
