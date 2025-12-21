import socket
import threading
from proxy_common import pipe
from config import *

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        d = sock.recv(1)
        if not d:
            raise ConnectionError
        buf += d
    return buf.decode(errors="ignore").strip()

def handle_peer(code, pid):
    print(f"[HOST] peer {pid} 데이터 채널 연결 중")

    data = socket.socket()
    data.connect((ORACLE_HOST, ORACLE_PORT))
    data.sendall(f"DATA HOST {code} {pid}\n".encode())

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))

    print(f"[HOST] peer {pid} 터널 시작")

    threading.Thread(
        target=pipe,
        args=(data, mc, f"relay{pid}->mc"),
        daemon=True
    ).start()

    threading.Thread(
        target=pipe,
        args=(mc, data, f"mc->relay{pid}"),
        daemon=True
    ).start()

def start_host(code):
    ctrl = socket.socket()
    ctrl.connect((ORACLE_HOST, ORACLE_PORT))
    ctrl.sendall(f"HOST {code}\n".encode())

    print(f"[HOST] HOST 등록 완료: {code}")
    print("[HOST] peer 대기 중...")

    while True:
        try:
            line = recv_line(ctrl)
        except ConnectionError:
            print("[HOST] control 채널 종료")
            break

        if not line:
            continue

        parts = line.split()

        if parts[0] == "NEW_PEER" and len(parts) >= 2:
            pid = parts[1]
            print(f"[HOST] 신규 PEER 접속: {pid}")
            handle_peer(code, pid)

        elif parts[0] in ("HOST_OK",):
            continue

        else:
            print("[HOST] 알 수 없는 control 메시지:", line)
