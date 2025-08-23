# Lecture 1: OpenCV 이미지 전처리 실습 가이드

이 문서는 YOLO와 같은 딥러닝 모델에 이미지를 입력하기 전, OpenCV를 활용하여 전처리를 수행하는 주요 기법들을 정리한 실습 가이드입니다. 각 기법에 대한 개념과 예제 코드를 단계적으로 소개합니다.

## 목차
- [Lecture 1: OpenCV 이미지 전처리 실습 가이드](#lecture-1-opencv-이미지-전처리-실습-가이드)
  - [OpenCV란?](#opencv란)
  - [설치 방법](#설치-방법)
    - [1단계: 터미널(명령 프롬프트) 열기](#1단계-터미널명령-프롬프트-열기)
    - [2단계: pip로 OpenCV 설치하기](#2단계-pip로-opencv-설치하기)
  - [matplotlib이란?](#matplotlib이란)
  - [설치 방법](#설치-방법-1)
  - [목차](#목차)
  - [1. 이미지 불러오기와 보여주기](#1-이미지-불러오기와-보여주기)
    - [실습 경로 설정 팁](#실습-경로-설정-팁)
  - [2. 블러 처리 (Blur)](#2-블러-처리-blur)
    - [2.1 평균 블러 (Average Blur)](#21-평균-블러-average-blur)
    - [2.2 가우시안 블러 (Gaussian Blur)](#22-가우시안-블러-gaussian-blur)
    - [2.3 미디안 블러 (Median Blur)](#23-미디안-블러-median-blur)
    - [2.4 양방향 필터 (Bilateral Filter)](#24-양방향-필터-bilateral-filter)
    - [2.5 블러 처리 요약 및 정리](#25-블러-처리-요약-및-정리)
  - [3. 엣지 검출 (Canny Edges)](#3-엣지-검출-canny-edges)
    - [1단계: Grayscale 변환](#1단계-grayscale-변환)
    - [2단계: Gaussian Blur 적용](#2단계-gaussian-blur-적용)
    - [3단계: Canny Edge Detection](#3단계-canny-edge-detection)
  - [4. 윤곽선 추출 (Contours)](#4-윤곽선-추출-contours)
    - [1단계: 이미지 로드 및 Grayscale 변환](#1단계-이미지-로드-및-grayscale-변환)
    - [2단계: Gaussian Blur 적용 + Canny 엣지 검출](#2단계-gaussian-blur-적용--canny-엣지-검출)
    - [3단계: 윤곽선 추출 및 시각화](#3단계-윤곽선-추출-및-시각화)
    - [함수 설명:](#함수-설명)
  - [5. 바운딩 박스 (Bounding Box)](#5-바운딩-박스-bounding-box)
    - [1단계: 이미지 불러오기 및 전처리](#1단계-이미지-불러오기-및-전처리)
    - [2단계: 윤곽선 추출](#2단계-윤곽선-추출)
    - [3단계: 바운딩 박스 그리기](#3단계-바운딩-박스-그리기)
    - [함수 설명](#함수-설명-1)
  - [6. 마무리](#6-마무리)
    - [학습한 주요 기법 요약](#학습한-주요-기법-요약)


## OpenCV란?

OpenCV(Open Source Computer Vision Library)는 실시간 컴퓨터 비전 및 이미지 처리에 사용되는 오픈소스 라이브러리입니다. Python, C++, Java 등 다양한 언어를 지원하며, 객체 인식, 얼굴 검출, 이미지 필터링, 윤곽선 추출 등의 작업에 활용됩니다.

- 공식 사이트: [https://opencv.org](https://opencv.org)
- Python에서 주로 사용하는 모듈 이름: `cv2`

## 설치 방법

OpenCV와 matplotlib은 Python 환경에서 이미지 전처리와 시각화를 위한 필수 라이브러리입니다. 아래의 단계에 따라 설치할 수 있습니다.

### 1단계: 터미널(명령 프롬프트) 열기

운영체제에 따라 아래 방법으로 명령어 입력창을 엽니다:

- **Windows**: 시작 메뉴에서 "명령 프롬프트" 또는 "cmd" 검색 후 실행
- **macOS**: Spotlight에서 "Terminal" 검색 후 실행
- **Linux**: Ctrl + Alt + T 또는 애플리케이션 메뉴에서 "터미널" 실행

### 2단계: pip로 OpenCV 설치하기

```bash
pip install opencv-python
```

OpenCV를 사용하려면 Python 파일 가장 위에 다음과 같이 cv2 모듈을 import해야 합니다:

```python
import cv2
```
이 줄이 빠지면 OpenCV 함수들을 사용할 수 없습니다.


## matplotlib이란?
matplotlib은 Python에서 이미지나 그래프를 시각화할 때 사용하는 라이브러리입니다.
OpenCV는 기본적으로 `cv2.imshow()`로 GUI 창을 띄우지만, 여러 이미지의 결과를 비교하기 위해서는 `matplotlib.pyplot`을 사용하는 것이 더 유용합니다.

## 설치 방법
터미널(명령 프롬프트)에서 아래 명령어로 설치할 수 있습니다:

```bash
pip install matplotlib
```

이제부터는 OpenCV를 이용해 이미지를 불러오고, 처리하고, 시각화하는 방법을 단계적으로 배워보겠습니다.



## 1. 이미지 불러오기와 보여주기
OpenCV에서 이미지를 불러오고 보여주는 가장 기본적인 기능입니다. 이후 모든 전처리 작업의 시작점입니다.

- `cv2.imread(path)` : 이미지를 BGR 형식으로 불러오기

- `cv2.imshow(window_name, image)` : 이미지를 새로운 창에 출력하여 시각적으로 확인할 수 있도록 함

**예제코드(1_imshow.py):**
```python
# 이미지 파일 경로
image_path = 'img/sample.jpg'

# 이미지를 컬러(BGR)로 불러오기
img = cv2.imread(image_path)

# 이미지가 잘 불러와졌는지 확인
if img is None:
    print("이미지를 불러오지 못했습니다.")
else:
    print("이미지 크기:", img.shape)  # (높이, 너비, 채널)

# 이미지 보여주기
cv2.imshow("Original Image", img)  # 새 창에 이미지 출력
cv2.waitKey(0)                      # 키 입력을 기다림 (무한 대기)
cv2.destroyAllWindows()            # 열린 모든 창 닫기
```

### 실습 경로 설정 팁
OpenCV에서 이미지 파일을 상대 경로(`img/sample.jpg`)로 불러오는 경우, 터미널에서 Python 파일이 위치한 디렉토리로 먼저 이동해야 합니다.

예를 들어 `Day4/1_opencv/` 폴더에 `1_imshow.py`와 `img/` 폴더가 함께 있다면 아래와 같이 경로를 이동한 후 실행하세요:

```bash
cd Day4/1_opencv
python 1_imshow.py
```
이 과정을 생략하면 `cv2.imread()`가 이미지를 찾지 못해 None을 반환하게 됩니다.


## 2. 블러 처리 (Blur)
이미지의 노이즈를 줄이거나 엣지를 부드럽게 만들기 위해 사용합니다. OpenCV에서는 다양한 종류의 블러 기법을 제공합니다.

### 2.1 평균 블러 (Average Blur)
주변 픽셀들의 **평균값**으로 현재 픽셀을 대체하는 방식입니다. 
처리 속도가 빠르지만, 엣지(경계) 정보가 많이 손실될 수 있습니다.

**파라미터:**
- `img`: 입력 이미지  
- `ksize`: 커널 크기 (예: `(5, 5)`) — 블러의 강도를 결정하는 요소

**예제 코드(2_blur.py):**
```python
blur_avg = cv2.blur(img, (5, 5))
```

### 2.2 가우시안 블러 (Gaussian Blur)
중심에 가까운 픽셀에 더 **높은 가중치**를 부여하는 방식입니다. 자연스럽고 부드러운 흐림 효과를 제공하며, 노이즈 제거에 효과적입니다.

**파라미터:**
- `img`: 입력 이미지  
- `ksize`: 커널 크기 (예: `(5, 5)`) — 가로, 세로 모두 홀수여야 함  
- `sigma`: X축 방향의 표준 편차 (`0`이면 자동 계산)

**예제 코드(2_blur.py):**
```python
blur_gaussian = cv2.GaussianBlur(img, (5, 5), 0)
```

### 2.3 미디안 블러 (Median Blur)
커널 내 픽셀 값의 **중간값**으로 현재 픽셀을 대체합니다. 점 형태의 노이즈(salt-and-pepper noise)에 강한 필터입니다.

**파라미터:**
- `img`: 입력 이미지 (grayscale 또는 color)  
- `ksize`: 필터 크기 (양의 홀수, 예: `3`, `5`, `7` 등)

**예제 코드(2_blur.py):**
```python
blur_median = cv2.medianBlur(img, ksize)
```
미디안 블러에서 ksize는 홀수여야 합니다. 따라서 다음과 같은 조건문을 사용하여 유효성을 검사하는 것이 좋습니다

**예제 코드(2_blur.py):**
```python
# ksize가 홀수가 아니라면 error 메시지를 띄운다.
if ksize % 2 == 1:
    blur_median = cv2.medianBlur(img, ksize)
else:
    raise ValueError("MedianBlur requires an odd ksize (3, 5, 7, ...).")
```

### 2.4 양방향 필터 (Bilateral Filter)
양방향 필터는 **공간적인 거리**와 **색상 차이**를 모두 고려하여 엣지를 보존하면서 흐림 효과를 주는 고급 블러 기법입니다. 엣지를 유지해야 하는 상황(예: 얼굴 보정, 배경 흐림 등)에 적합하지만, 계산량이 많아 속도가 느릴 수 있습니다.

**파라미터:**
- `img`: 입력 이미지  
- `d`: 필터링에 사용할 이웃 픽셀의 지름  
- `sigmaColor`: 색상 차이에 대한 필터의 표준 편차 (값이 클수록 더 많은 색상 차이 허용)  
- `sigmaSpace`: 거리 차이에 대한 필터의 표준 편차 (값이 클수록 더 멀리 떨어진 픽셀도 영향을 줌)

**예제 코드(2_blur.py):**
```python
blur_bilateral = cv2.bilateralFilter(img, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)
```

### 2.5 블러 처리 요약 및 정리

블러 처리는 이미지의 **노이즈를 줄이고**, **윤곽선을 부드럽게 만드는** 중요한 전처리 과정입니다. OpenCV에서는 다양한 방식의 블러 기법을 제공하며, 각 방식은 용도에 따라 선택됩니다

- **Average Blur**: 단순하고 빠르지만 엣지 보존이 어려움  
- **Gaussian Blur**: 자연스러운 흐림, 가장 일반적인 선택  
- **Median Blur**: salt-and-pepper 노이즈 제거에 효과적  
- **Bilateral Filter**: 엣지를 보존하며 흐림 효과를 주는 고급 필터

---

다음 섹션에서는 이러한 블러 처리 이후의 단계인  
**엣지 검출(Canny Edge Detection)** 에 대해 알아보겠습니다.



## 3. 엣지 검출 (Canny Edges)

이미지의 **경계(윤곽선)** 을 검출하여 객체의 구조나 형태를 파악하는 데 사용됩니다.
OpenCV의 Canny 엣지 검출은 일반적으로 다음과 같은 전처리 단계를 거친 후 수행합니다.

**예제코드(3_canny_edges.py):**

### 1단계: Grayscale 변환 
컬러 이미지를 흑백 이미지로 변환하여 채널 수를 줄이고 계산 효율을 높입니다.

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
```

### 2단계: Gaussian Blur 적용  
노이즈로 인한 잘못된 엣지 검출을 방지하기 위해 흐림 처리를 수행합니다.

```python
blur = cv2.GaussianBlur(gray, (5, 5), 0)
```

### 3단계: Canny Edge Detection  
실제 엣지를 추출하는 단계입니다.

```python
edges = cv2.Canny(blur, threshold1, threshold2)
```

**파라미터 설명:**
- `blur`: 입력 이미지 (보통 Gaussian Blur 처리된 흑백 이미지)  
- `threshold1`: 낮은 임계값 (약한 엣지 경계 기준)  
- `threshold2`: 높은 임계값 (강한 엣지 경계 기준)


두 임계값 사이의 경계를 가진 픽셀은 **주변에 강한 엣지가 있을 경우 엣지로 간주**됩니다. 일반적으로 `threshold1 < threshold2` 여야 하며, 실험을 통해 최적값을 찾는 것이 중요합니다.


## 4. 윤곽선 추출 (Contours)

윤곽선(Contour)은 동일한 색상이나 강도를 가진 픽셀들이 연결된 곡선을 의미하며, 객체의 외형을 파악하거나 바운딩 박스를 생성하는 데 사용됩니다. 윤곽선 추출을 위해선 먼저 Canny 엣지 검출 등의 방식으로 경계선을 확보해야 합니다.

**예제코드(4_contours.py):**  

### 1단계: 이미지 로드 및 Grayscale 변환

```python
img = cv2.imread('img/sample.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
```

### 2단계: Gaussian Blur 적용 + Canny 엣지 검출

```python
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)
```

### 3단계: 윤곽선 추출 및 시각화

```python
# 컨투어 추출
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 컨투어 시각화
img_contour = img.copy()
contour_color = (180, 100, 50)
cv2.drawContours(img_contour, contours, -1, contour_color, 2)
```

### 함수 설명:

- `cv2.findContours()` : 엣지를 기준으로 윤곽선 리스트를 추출합니다.  
- `cv2.drawContours()` : 추출한 윤곽선을 이미지 위에 시각화합니다.  
- `cv2.RETR_EXTERNAL` : 외곽 윤곽선만 찾도록 설정합니다.  
- `cv2.CHAIN_APPROX_SIMPLE` : 윤곽선을 단순화하여 메모리를 절약합니다.

이렇게 추출한 윤곽선은 **도형 분류, 바운딩 박스 생성** 등 다양한 후처리 작업에 유용하게 사용됩니다.


## 5. 바운딩 박스 (Bounding Box)

윤곽선(contour)로부터 객체를 감싸는 **사각형을 생성**해 ROI(관심 영역)를 지정하는 기법입니다. 객체 탐지, 추적, 분할 등에서 자주 사용되며, OpenCV에서는 수평 바운딩 박스와 회전된 최소 바운딩 박스를 모두 제공합니다.

**예제코드(5_bounding_boxes.py):**  

### 1단계: 이미지 불러오기 및 전처리

```python
img = cv2.imread('img/shapes.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)
```

이미지를 불러온 뒤 그레이스케일로 변환하고,  
Gaussian Blur로 노이즈를 제거한 후 Canny 엣지 검출을 수행합니다.

### 2단계: 윤곽선 추출

```python
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```

외곽 윤곽선만 추출하여 바운딩 박스를 적용할 대상을 찾습니다.

### 3단계: 바운딩 박스 그리기

```python
img_bbox = img.copy()

for contour in contours:
    # 일반 바운딩 박스 (빨간색)
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img_bbox, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 회전된 바운딩 박스 (초록색)
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = box.astype(int)
    cv2.drawContours(img_bbox, [box], 0, (0, 255, 0), 2)
```

### 함수 설명

- `cv2.boundingRect(contour)` : 수평/수직으로 정렬된 가장 작은 사각형 반환  
- `cv2.rectangle()` : 해당 사각형을 이미지에 그리기  
- `cv2.minAreaRect(contour)` : 회전까지 고려한 최소 영역 사각형 반환 (중심, 각도 포함)  
- `cv2.boxPoints()` : `minAreaRect` 결과를 꼭짓점 좌표로 변환  
- `cv2.drawContours()` : 꼭짓점 좌표를 기반으로 회전된 박스 시각화

각 방식은 사용하는 목적에 따라 선택됩니다:  
- 수직/수평 정렬된 영역을 기준으로 자르려면 **`boundingRect()`**  
- 회전된 물체의 외곽까지 정확하게 감싸고 싶을 땐 **`minAreaRect()`**



## 6. 마무리

OpenCV를 활용한 주요 **이미지 전처리 기법**들을 단계적으로 살펴보았습니다. 각 단계는 딥러닝 모델의 입력 데이터를 준비하거나, 기초적인 영상 분석 작업의 기반을 마련하는 데 **필수적인 요소**들입니다.

### 학습한 주요 기법 요약

- **이미지 불러오기와 시각화** (`cv2.imread`, `cv2.imshow`)  
- **다양한 블러 처리** (Average, Gaussian, Median, Bilateral)  
- **Canny 엣지를 이용한 경계 검출**  
- **윤곽선(Contours)을 이용한 구조 추출**  
- **바운딩 박스를 활용한 객체 감싸기**

이러한 기법들을 조합하면 **객체 탐지, 이미지 필터링, 모양 분석** 등 더 복잡한 영상 처리 프로젝트를 구현할 수 있습니다.
