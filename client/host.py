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

def handle_peer(pid):
    data = socket.socket()
    data.connect((ORACLE_HOST, ORACLE_PORT))
    data.sendall(f"DATA {pid}\n".encode())

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))

    start_pipe(data, mc, f"relay{pid}->mc")
    start_pipe(mc, data, f"mc->relay{pid}")

def start_host(code):
    ctrl = socket.socket()
    ctrl.connect((ORACLE_HOST, ORACLE_PORT))
    ctrl.sendall(f"HOST {code}\n".encode())
    print(f"[HOST] HOST 등록 완료: {code}")

    while True:
        line = recv_line(ctrl)
        parts = line.split()

        if parts[0] == "HOST_OK":
            print("[HOST] 릴레이 등록 확인 완료")
            continue

        if parts[0] == "NEW_PEER":
            pid = int(parts[1])
            print(f"[HOST] 신규 PEER 접속: {pid}")
            threading.Thread(target=handle_peer, args=(pid,), daemon=True).start()
