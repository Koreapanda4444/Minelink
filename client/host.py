import socket
import threading
from config import *
from proxy_common import start_pipe

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        c = sock.recv(1)
        if not c:
            raise ConnectionError
        buf += c
    return buf.decode().strip()

def start_host(code):
    print("[HOST] connecting to relay...")
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"HOST {code}\n".encode())

    print("[HOST] waiting for peer...")
    msg = recv_line(relay)
    if msg != "PEER_JOINED":
        print("[HOST] unexpected:", msg)
        return

    peer_addr = recv_line(relay)
    print("[HOST] peer connected:", peer_addr)

    print("[HOST] connecting to minecraft server...")
    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))
    print("[HOST] minecraft connected")

    print("[HOST] starting RAW tunnel")
    start_pipe(relay, mc, "relay->mc")
    start_pipe(mc, relay, "mc->relay")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("[HOST] exit")
