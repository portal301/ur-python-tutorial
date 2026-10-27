# Lecture 1
## 강의 목표
- Docker Desktop을 설치합니다.
- URSim을 쓰는 데 필요한 Docker 개념 네 가지(이미지, 컨테이너, 포트 연결, 폴더 연결)를 익힙니다.

## 1. Docker Desktop 설치
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)을 내려받아 설치합니다. (관리자 권한 필요)
2. 설치 중 **WSL 2 사용** 옵션을 켜 둡니다.
3. 설치가 끝나면 Docker Desktop을 실행하고, 터미널(PowerShell)에서 확인합니다.
```powershell
docker --version
```
> 이 과정의 명령은 모두 **PowerShell**에서 실행합니다. Git Bash에서는 경로가 바뀌어 동작이 달라집니다.

설치가 안 되면 BIOS에서 **가상화(VT-x / AMD-V)** 가 켜져 있는지 확인해 주세요.

## 2. 이미지와 컨테이너
- **이미지**: 프로그램과 실행 환경을 통째로 담은 설치 파일 같은 것입니다. 내려받아 두면 계속 씁니다.
- **컨테이너**: 이미지를 실행한 것입니다. 하나의 이미지로 컨테이너를 여러 개 띄울 수 있습니다.

```powershell
docker run hello-world
```
`hello-world` 이미지가 없으면 자동으로 내려받고, 컨테이너를 실행해 인사말을 출력한 뒤 종료합니다.

```powershell
docker images     # 내려받은 이미지 목록
docker ps -a      # 컨테이너 목록 (-a: 종료된 것까지)
```

## 3. 포트 연결 (`-p`)
컨테이너는 내 PC와 분리된 작은 컴퓨터처럼 동작합니다. 컨테이너 안의 포트를 내 PC에서 쓰려면 연결해 줘야 합니다.

```powershell
docker run --rm -p 8080:80 nginx
```
- `-p 8080:80`: 내 PC의 8080번 포트 → 컨테이너의 80번 포트
- `--rm`: 컨테이너를 끄면 자동으로 지움

브라우저에서 `http://localhost:8080` 에 접속해 nginx 환영 페이지가 뜨면 성공입니다. 터미널에서 `Ctrl + C` 로 끕니다.

> Lecture 2에서 URSim의 30001번 포트를 내 PC의 30001번에 연결하는 것도 같은 원리입니다.

## 4. 폴더 연결 (`-v`)
컨테이너는 끄면 안에서 만든 파일이 사라집니다. 내 PC의 폴더를 컨테이너에 연결하면 파일이 남습니다.

1. 빈 폴더를 만들고 그 안에 `index.html` 을 VSCode로 만듭니다.
```html
<h1>Hello Docker</h1>
```
2. 그 폴더에서 실행합니다.
```powershell
docker run --rm -p 8080:80 -v ${PWD}:/usr/share/nginx/html nginx
```
- `-v 내PC폴더:컨테이너폴더`: `${PWD}` 는 PowerShell에서 현재 폴더를 뜻합니다.

브라우저에서 `http://localhost:8080` 에 `Hello Docker` 가 보이면 성공입니다. `index.html` 을 고치고 새로고침하면 바로 바뀝니다.

> Lecture 2에서 PolyScope 프로그램을 남기는 데 이 방법을 씁니다.
