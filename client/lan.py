import socket
import threading
from network import network
from state import state

MC_LAN_PORT = 4445
BUFFER_SIZE = 2048

class LanEmulator:
    def start_sniff(self):
        if not state.is_host():
            return
        t = threading.Thread(target=self._sniff_loop, daemon=True)
        t.start()
        print("LAN sniff started (UDP capture)")

    def _sniff_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", MC_LAN_PORT))

        while state.is_host():
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                payload = {
                    "type": "lan_packet",
                    "data": data.hex()
                }
                network.send(payload)
            except Exception:
                continue

    def emit(self, payload):
        if not state.is_peer():
            return
        if not isinstance(payload, dict):
            return
        if payload.get("type") != "lan_packet":
            return

        try:
            data = bytes.fromhex(payload.get("data"))
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(data, ("255.255.255.255", MC_LAN_PORT))
            sock.close()
        except Exception:
            pass

lan = LanEmulator()
