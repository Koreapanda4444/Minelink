import socket
from proxy_common import ProxyConnection
from mc_packets import parse_packet_id, parse_status_response


def start_peer():
    listen = socket.socket()
    listen.bind(("127.0.0.1", 25565))
    listen.listen(1)

    client, _ = listen.accept()

    relay = socket.socket()
    relay.connect(("127.0.0.1", 9000))

    state = {"mode": None}

    def on_client(packet):
        pid = parse_packet_id(packet)
        if pid == 0x00:
            state["mode"] = "STATUS"

    def on_server(packet):
        if state["mode"] == "STATUS":
            data = parse_status_response(packet)
            if data:
                print(data)

    ProxyConnection(
        client,
        relay
    ).start(hook_a=on_client, hook_b=on_server)
