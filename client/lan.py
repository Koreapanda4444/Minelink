import socket
import threading
from network import network
from state import state

MC_LAN_PORT = 4445
MC_TCP_PORT = 25565
BUFFER_SIZE = 4096

class LanEmulator:
    def start_sniff(self):
        if not state.is_host():
            return
        t = threading.Thread(target=self._sniff_loop, daemon=True)
        t.start()

    def _sniff_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", MC_LAN_PORT))

        while state.is_host():
            data, _ = sock.recvfrom(2048)
            network.send({
                "type": "lan_packet",
                "data": data.hex()
            })

    def emit(self, payload):
        if payload.get("type") == "lan_packet" and state.is_peer():
            data = bytes.fromhex(payload["data"])
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(data, ("255.255.255.255", MC_LAN_PORT))
            s.close()

    def start_tcp_proxy(self):
        if not state.is_peer():
            return
        t = threading.Thread(target=self._tcp_proxy_loop, daemon=True)
        t.start()
        print("TCP proxy listening on localhost:25565")

    def _tcp_proxy_loop(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", MC_TCP_PORT))
        server.listen(1)

        while True:
            client, _ = server.accept()
            threading.Thread(
                target=self._handle_client,
                args=(client,),
                daemon=True
            ).start()

    def _handle_client(self, client):
        while True:
            data = client.recv(BUFFER_SIZE)
            if not data:
                break
            network.send({
                "type": "tcp_data",
                "data": data.hex()
            })
        client.close()

lan = LanEmulator()
