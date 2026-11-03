"""URSim(도커)으로 .script 파일의 오타/문법 오류를 검사하는 스크립트

사용법:
    python check_script.py 파일.script

필요: Docker Desktop 실행 중 + universalrobots/ursim_e-series 이미지
처음 실행하면 URSim 컨테이너를 띄우고(수십 초), 이후에는 바로 검사합니다.
검사 대상: def 이름(): ... end 하나로 감싼 스크립트
"""
import re
import socket
import struct
import subprocess
import sys
import time

HOST = "127.0.0.1"
CONTAINER = "ursim_e"
IMAGE = "universalrobots/ursim_e-series"
PORTS = ["29999", "30001", "30002", "30003", "30004", "6080"]
LOG = "/ursim/URControl.log"
LOG_ERROR = re.compile(r"Compile error|Syntax error|Parse Error|Lexer exception", re.I)

sys.stdout.reconfigure(errors="replace")


# ---------- 1. URSim 컨테이너 준비 ----------
def docker(*args):
    try:
        return subprocess.run(["docker", *args], capture_output=True,
                              encoding="utf-8", errors="replace")
    except FileNotFoundError:
        raise RuntimeError("docker 명령을 찾을 수 없습니다. Docker Desktop을 설치하세요.")


def ensure_ursim():
    r = docker("ps", "-a", "--filter", f"name=^{CONTAINER}$", "--format", "{{.State}}")
    if r.returncode != 0:
        sys.exit("Docker가 실행 중이 아닙니다. Docker Desktop을 켜주세요.")
    state = r.stdout.strip()
    if state == "running":
        return
    if state:  # 컨테이너는 있는데 꺼져 있음
        print("URSim 컨테이너 시작 중...")
        r = docker("unpause" if state == "paused" else "start", CONTAINER)
    else:
        print("URSim 컨테이너 생성 중... (처음 한 번만)")
        cmd = ["run", "-d", "--name", CONTAINER]
        for p in PORTS:
            cmd += ["-p", f"{p}:{p}"]
        r = docker(*cmd, IMAGE)
    if r.returncode != 0:
        sys.exit("URSim 컨테이너 실행 실패 (다른 URSim이 같은 포트를 쓰고 있는지 확인):\n" + r.stderr)


def wait_ready(timeout=180):
    """대시보드(29999)가 응답하면 URSim 준비 완료로 판단"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = None
        try:
            s = socket.create_connection((HOST, 29999), timeout=2)
            if s.recv(1024):
                return
        except OSError:
            pass
        finally:
            if s:
                s.close()
        print(f"\rURSim 부팅 대기 중... {int(time.time() - t0)}초", end="", flush=True)
        time.sleep(2)
    sys.exit("\nURSim이 응답하지 않습니다.")


def log_lines():
    r = docker("exec", CONTAINER, "cat", LOG)
    return r.stdout.splitlines() if r.returncode == 0 else []


# ---------- 2. 파일 읽기 + 구조 확인 ----------
def read_script(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):  # 메모장 'UTF-8(BOM)' 저장 시 붙는 표시 제거
        raw = raw[3:]
    for enc in ("utf-8", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    sys.exit("파일 인코딩을 읽을 수 없습니다. UTF-8로 저장해 주세요.")


def find_def(lines):
    """def ... end 하나로 감싸져 있는지 확인하고 def 줄 번호(1부터)를 돌려줌"""
    code = [(i + 1, l) for i, l in enumerate(lines)
            if l.strip() and not l.strip().startswith("#")]
    defs = [n for n, l in code if re.match(r"def\s", l)]
    problem = None
    if not code:
        problem = "파일이 비어 있습니다."
    elif not re.match(r"def\s", code[0][1]):
        problem = f"{code[0][0]}번째 줄: 첫 코드가 'def 이름():' 이어야 합니다."
    elif len(defs) > 1:
        problem = f"{defs[1]}번째 줄: 맨 앞(들여쓰기 없음)에 def가 또 있습니다. 하나로 감싸 주세요."
    elif not re.fullmatch(r"end\s*(#.*)?", code[-1][1]):
        problem = f"{code[-1][0]}번째 줄: 마지막 줄이 들여쓰기 없는 'end'여야 합니다."
    if problem:
        print(f"[오류] 구조 문제 - {problem}")
        print("  스크립트 전체를 def 이름(): ... end 하나로 감싸야 로봇에서 실행됩니다.")
        sys.exit(1)
    return defs[0]


# ---------- 3. 스크립트 보내고 컴파일 결과 받기 ----------
def compile_check(code):
    """30001로 보내고, 돌아오는 런타임 예외 메시지(줄, 칸, 내용)를 모은다"""
    try:
        s = socket.create_connection((HOST, 30001), timeout=3)
    except OSError:
        sys.exit("URSim(30001)에 연결할 수 없습니다. 잠시 후 다시 실행하세요.")
    s.sendall(code.encode() + b"\n")
    s.settimeout(0.3)
    buf, errors, got_hello, t0 = b"", [], False, time.time()
    while time.time() - t0 < 3 and not errors:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
        except socket.timeout:
            pass
        # 패킷 단위로 자르기: [길이 4바이트][타입 1바이트][본문]
        while len(buf) >= 5:
            size, ptype = struct.unpack(">iB", buf[:5])
            if size < 5:
                buf = b""
                break
            if len(buf) < size:
                break
            body, buf = buf[5:size], buf[size:]
            if ptype == 20 and len(body) >= 10:
                if body[9] == 3:  # 접속 시 오는 버전 메시지 = 컨트롤러가 살아 있음
                    got_hello = True
                # 10 = 런타임 예외(컴파일 에러 포함)
                if body[9] == 10 and len(body) >= 18:
                    line, col = struct.unpack(">ii", body[10:18])
                    errors.append((line, col, body[18:].decode(errors="replace")))
    s.close()
    if not got_hello:
        sys.exit("검사 실패: URSim 컨트롤러가 응답하지 않습니다. 잠시 후 다시 실행하세요.")
    return errors


# ---------- 4. 읽기 쉽게 출력 ----------
def explain(text):
    parts = text.strip(":").split(":")
    if parts[0] == "compile_error_name_not_found" and len(parts) > 1:
        return f"'{parts[1]}' 라는 이름이 없습니다 (함수/변수 이름 오타?)"
    if parts[0] == "syntax_error_on_line":
        return "문법 오류 (괄호, end, 콜론 등 확인. 실제 실수는 이 줄 바로 위일 수 있음)"
    return text


def main():
    if len(sys.argv) != 2:
        sys.exit("사용법: python check_script.py 파일.script")
    path = sys.argv[1]
    code = read_script(path)
    lines = code.splitlines()
    def_line = find_def(lines)

    ensure_ursim()
    wait_ready()

    n_before = len(log_lines())
    errors = compile_check(code)
    time.sleep(0.3)
    log_errors = [l for l in log_lines()[n_before:] if LOG_ERROR.search(l)]

    if not errors and not log_errors:
        print(f"\nOK: {path} 컴파일 오류 없음")
        return
    for line, col, text in errors:
        # 컨트롤러는 def 줄을 1번으로 셈 → 파일 기준 줄 번호로 변환
        n = def_line + line - 1
        print(f"\n[오류] {path} {n}번째 줄: {explain(text)}")
        for k in range(max(1, n - 1), min(len(lines), n) + 1):
            mark = ">>" if k == n else "  "
            print(f"  {mark} {k:4d} | {lines[k - 1]}")
    if not errors:  # 30001로는 안 왔지만 로그에는 남은 경우
        print(f"\n[오류] {path} (URControl.log)")
        for l in log_errors:
            print("  " + l.split(" - ", 1)[-1])
    sys.exit(1)


if __name__ == "__main__":
    main()
