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
    return buf.decode().strip()


def handle_peer(pid, data_listener):
    print(f"[HOST] peer {pid} 데이터 채널 대기 중")

    data_sock, addr = data_listener.accept()
    print(f"[HOST] peer {pid} 데이터 채널 연결됨: {addr}")

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))
    print(f"[HOST] peer {pid} → 로컬 마크 서버 연결 완료")

    threading.Thread(
        target=pipe,
        args=(data_sock, mc, f"relay{pid}->mc"),
        daemon=True
    ).start()

    threading.Thread(
        target=pipe,
        args=(mc, data_sock, f"mc->relay{pid}"),
        daemon=True
    ).start()


def start_host(code):
    ctrl = socket.socket()
    ctrl.connect((ORACLE_HOST, ORACLE_PORT))
    ctrl.sendall(f"HOST {code}\n".encode())
    print(f"[HOST] HOST 등록 완료: {code}")

    data_listener = socket.socket()
    data_listener.bind(("0.0.0.0", 0))
    data_listener.listen()
    data_port = data_listener.getsockname()[1]

    print(f"[HOST] 데이터 채널 대기 포트: {data_port}")

    ctrl.sendall(f"DATA_PORT {data_port}\n".encode())

    print("[HOST] peer 대기 중...")

    while True:
        line = recv_line(ctrl)
        parts = line.split()

        if parts[0] == "HOST_OK":
            print("[HOST] 릴레이 등록 확인 완료")
            continue

        if parts[0] == "NEW_PEER":
            pid = parts[1]
            print(f"[HOST] 신규 PEER 접속: {pid}")
            threading.Thread(
                target=handle_peer,
                args=(pid, data_listener),
                daemon=True
            ).start()
            continue

        print(f"[HOST] 알 수 없는 control 메시지: {line}")
