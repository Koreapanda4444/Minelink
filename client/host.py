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

def handle_peer(pid, relay_addr):
    print(f"[HOST] peer {pid} data 채널 생성")
    data = socket.socket()
    data.connect(relay_addr)

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))

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

    while True:
        line = recv_line(ctrl)
        cmd, pid = line.split()
        if cmd == "NEW_PEER":
            print(f"[HOST] 신규 PEER 요청: {pid}")
            handle_peer(pid, ctrl.getsockname())
