import socket
from proxy_common import ProxyConnection
from mc_packets import parse_handshake


def start_peer():
    listen = socket.socket()
    listen.bind(("127.0.0.1", 25565))
    listen.listen(1)

    print("[peer] waiting for minecraft client...")
    client_sock, _ = listen.accept()

    relay = socket.socket()
    relay.connect(("127.0.0.1", 9000))

    def on_client_packet(packet):
        info = parse_handshake(packet)
        if info:
            print("[HANDSHAKE]", info)

    ProxyConnection(
        client_sock,
        relay,
        name="peer-proxy"
    ).start(hook_a=on_client_packet)
