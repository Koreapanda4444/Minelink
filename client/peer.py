import socket
from proxy_common import ProxyConnection
from mc_packets import parse_packet_id, parse_status_response, parse_disconnect


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
        if pid == 0x00 and state["mode"] == "STATUS":
            pass
        if pid == 0x00 and state["mode"] != "STATUS":
            state["mode"] = "LOGIN"

    def on_server(packet):
        pid = parse_packet_id(packet)

        if state["mode"] == "STATUS":
            data = parse_status_response(packet)
            if data:
                print(data)

        if state["mode"] == "LOGIN":
            msg = parse_disconnect(packet)
            if msg:
                print(msg)

    ProxyConnection(
        client,
        relay
    ).start(hook_a=on_client, hook_b=on_server)
