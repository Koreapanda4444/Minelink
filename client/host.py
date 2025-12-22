import socket
import threading
from proxy_common import start_pipe
from config import *

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        d = sock.recv(1)
        if not d:
            raise ConnectionError
        buf += d
    return buf.decode().strip()

def handle_peer(data_sock, pid):
    print(f"[HOST] peer {pid} 연결됨")

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))
    print(f"[HOST] peer {pid} → minecraft 연결")

    start_pipe(data_sock, mc, f"relay{pid}->mc")
    start_pipe(mc, data_sock, f"mc->relay{pid}")

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

    while True:
        line = recv_line(ctrl)
        parts = line.split()

        if parts[0] == "HOST_OK":
            print("[HOST] 릴레이 등록 확인 완료")
            continue

        if parts[0] == "NEW_PEER":
            pid = parts[1]
            print(f"[HOST] 신규 PEER 접속: {pid}")

            data_sock, _ = data_listener.accept()
            threading.Thread(
                target=handle_peer,
                args=(data_sock, pid),
                daemon=True
            ).start()
