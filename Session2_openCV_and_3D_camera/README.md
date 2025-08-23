# Session2: 컴퓨터 비전과 3D 인식 기초

Day4에서는 **컴퓨터 비전**과 **3D 인식**의 기초를 다루며, OpenCV 전처리부터 RealSense 카메라 활용, 카메라 보정(Camera Calibration)까지 학습합니다.  
각 강의는 실습 중심으로 진행되며, 로봇 비전과 물체 인식·조작(Pick-and-Place)의 기반 기술을 익히는 것을 목표로 합니다.

## 강의 구성

### 1. OpenCV 이미지 전처리 실습
- OpenCV와 matplotlib 설치 및 기본 사용법
- 이미지 불러오기 및 시각화
- 블러 처리 기법
  - Average Blur
  - Gaussian Blur
  - Median Blur
  - Bilateral Filter
- Canny 엣지 검출
- 윤곽선(Contours) 추출 및 시각화
- 바운딩 박스(Bounding Box) 생성

### 2. RealSense를 활용한 3차원 데이터 이해
- RealSense D435F 카메라 원리와 사용법
- 실시간 RGB + Depth 영상 수신 및 시각화
- Intrinsic 파라미터 확인 및 중심 픽셀 3D 위치 추출
- 마우스 클릭 기반 픽셀 → 3D 좌표 변환
- 6자유도(6DoF) 개념과 로봇 작업 적용 사례

### 3. Camera Calibration
- 카메라 왜곡(Radial, Tangential) 원리 이해
- 체커보드를 이용한 Intrinsic Parameter 계산
- 왜곡 계수를 활용한 이미지 보정
- 보정 전/후 비교 및 JSON 형식 파라미터 저장

## 기대 효과
- OpenCV를 활용해 이미지 전처리와 기본 객체 인식 기술 습득
- RealSense 카메라로 2D/3D 데이터 수집 및 처리 역량 강화
- 카메라 보정 원리와 실습을 통해 정확한 영상 데이터 확보 방법 이해
- 로봇 비전, 3D 인식, 물체 자세 추정의 기반 기술 습득
