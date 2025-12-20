import socket
from proxy_common import ProxyConnection
from mc_packets import parse_packet_id


def start_peer():
    listen = socket.socket()
    listen.bind(("127.0.0.1", 25565))
    listen.listen(1)

    client, _ = listen.accept()

    relay = socket.socket()
    relay.connect(("127.0.0.1", 9000))

    state = {"mode": None, "encrypted": False}

    def on_client(packet):
        pid = parse_packet_id(packet)
        if pid == 0x00 and state["mode"] is None:
            state["mode"] = "STATUS"
        elif pid == 0x00 and state["mode"] == "STATUS":
            state["mode"] = "LOGIN"

    def on_server(packet):
        pid = parse_packet_id(packet)

        if state["mode"] == "LOGIN" and pid == 0x01:
            state["encrypted"] = True

    ProxyConnection(
        client,
        relay
    ).start(hook_a=on_client, hook_b=on_server)
