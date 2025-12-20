import socket
from config import ORACLE_HOST, ORACLE_PORT, PEER_BIND_HOST, PEER_BIND_PORT
from proxy_common import ProxyConnection

def start_peer(code):
    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)

    client, _ = listen.accept()

    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())

    ProxyConnection(client, relay).start()
