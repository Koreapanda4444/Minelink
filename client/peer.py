import socket
from config import *
from proxy_common import start_pipe

def start_peer(code):
    print("[PEER] connecting to relay...")
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())

    resp = relay.recv(64).decode().strip()
    if resp != "JOIN_OK":
        print("[PEER] join failed:", resp)
        return

    print("[PEER] waiting for minecraft client...")
    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)

    mc, addr = listen.accept()
    print("[PEER] minecraft connected:", addr)

    print("[PEER] starting RAW tunnel")
    start_pipe(mc, relay, "mc->relay")
    start_pipe(relay, mc, "relay->mc")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("[PEER] exit")
