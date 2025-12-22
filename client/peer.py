import socket
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

def start_peer(code):
    ctrl = socket.socket()
    ctrl.connect((ORACLE_HOST, ORACLE_PORT))
    ctrl.sendall(f"JOIN {code}\n".encode())

    line = recv_line(ctrl)
    _, pid = line.split()
    pid = int(pid)
    print(f"[PEER] JOIN 완료 (pid={pid})")

    data = socket.socket()
    data.connect((ORACLE_HOST, ORACLE_PORT))
    data.sendall(f"DATA {pid}\n".encode())

    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)
    print("[PEER] 마크 대기 중")

    mc, _ = listen.accept()
    print("[PEER] 마크 연결됨")

    start_pipe(data, mc, "relay->mc")
    start_pipe(mc, data, "mc->relay")
