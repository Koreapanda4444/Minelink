import socket
from config import ORACLE_HOST, ORACLE_PORT, MC_SERVER_HOST, MC_SERVER_PORT
from proxy_common import ProxyConnection

def start_host(code):
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"HOST {code}\n".encode())

    peer_info = relay.recv(128).decode().strip()
    print(f"[INFO] Peer connected: {peer_info}")

    server = socket.socket()
    server.connect((MC_SERVER_HOST, MC_SERVER_PORT))

    ProxyConnection(relay, server).start()
