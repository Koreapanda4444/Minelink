import socket
from proxy_common import start_pipe
from config import *

def start_peer(code):
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())

    resp = relay.recv(1024).decode().strip()
    _, pid, host_ip, host_port = resp.split()
    print(f"[PEER] JOIN 완료 (pid={pid})")

    data = socket.socket()
    data.connect((host_ip, int(host_port)))

    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)
    print("[PEER] minecraft 대기 중")

    mc, _ = listen.accept()
    print("[PEER] minecraft 연결됨")

    start_pipe(data, mc, "relay->mc")
    start_pipe(mc, data, "mc->relay")
