import socket
from proxy_common import pipe
from config import *

def start_peer(code):
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())

    resp = relay.recv(1024).decode().strip()
    _, pid = resp.split()
    print(f"[PEER] JOIN 완료 (pid={pid})")

    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)

    mc, _ = listen.accept()
    print("[PEER] minecraft 연결됨")

    pipe(relay, mc, "relay->mc")
    pipe(mc, relay, "mc->relay")
