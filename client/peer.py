import socket
from proxy_common import ProxyConnection
from mc_packets import parse_packet_id, is_login_success


def start_peer():
    listen = socket.socket()
    listen.bind(("127.0.0.1", 25565))
    listen.listen(1)

    while True:
        client, _ = listen.accept()

        relay = socket.socket()
        relay.connect(("127.0.0.1", 9000))

        state = {
            "phase": "HANDSHAKE",
            "encrypted": False,
            "play": False
        }

        def on_client(packet):
            if state["phase"] == "HANDSHAKE":
                state["phase"] = "AWAIT_SERVER"

        def on_server(packet):
            pid = parse_packet_id(packet)

            if state["phase"] == "AWAIT_SERVER":
                if pid == 0x00:
                    state["phase"] = "STATUS"
                else:
                    state["phase"] = "LOGIN"

            if state["phase"] == "LOGIN" and pid == 0x01:
                state["encrypted"] = True

            if state["phase"] == "LOGIN" and is_login_success(packet):
                state["phase"] = "PLAY"
                state["play"] = True
                print("PLAY")

        ProxyConnection(
            client,
            relay
        ).start(hook_a=on_client, hook_b=on_server)
