import socket
import threading
from proxy_common import pipe
from config import *

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError
        buf += chunk
    return buf.decode().strip()

def start_host(code):
    print("[HOST] connecting to relay...")
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"HOST {code}\n".encode())
    print(f"[HOST] registered as HOST (code={code})")

    print("[HOST] waiting for peer join...")

    line = recv_line(relay)
    print(f"[HOST] relay control message: {line}")

    if line != "PEER_JOINED":
        print("[HOST] unexpected control message, abort")
        return

    peer_addr = recv_line(relay)
    print(f"[HOST] peer connected from {peer_addr}")

    print("[HOST] connecting to local minecraft server...")
    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))
    print("[HOST] connected to minecraft server (25565)")

    print("[HOST] starting packet proxy")

    threading.Thread(target=pipe, args=(relay, mc, "relay->mc"), daemon=True).start()
    threading.Thread(target=pipe, args=(mc, relay, "mc->relay"), daemon=True).start()

    while True:
        try:
            cmd = recv_line(relay)
            print(f"[HOST][CTRL] {cmd}")
        except:
            print("[HOST] control channel closed")
            break
