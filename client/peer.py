import socket
import threading
from proxy_common import pipe
from config import *

def start_peer(code):
    print("[PEER] connecting to relay...")
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())
    print(f"[PEER] sent JOIN request (code={code})")

    listen = socket.socket()
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)

    print(f"[PEER] waiting for minecraft client on {PEER_BIND_PORT}...")

    mc, addr = listen.accept()
    print(f"[PEER] minecraft client connected from {addr}")

    print("[PEER] starting packet proxy")

    threading.Thread(target=pipe, args=(mc, relay, "mc->relay"), daemon=True).start()
    threading.Thread(target=pipe, args=(relay, mc, "relay->mc"), daemon=True).start()
