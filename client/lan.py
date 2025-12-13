import threading
import time
from network import network
from state import state

class LanEmulator:
    def start_sniff(self):
        if not state.is_host():
            return
        threading.Thread(target=self._sniff_loop, daemon=True).start()
        print("LAN sniff started")

    def _sniff_loop(self):
        while state.is_host():
            data = {"type": "lan_announce", "name": "Minecraft LAN Server"}
            network.send(data)
            time.sleep(2)

    def emit(self, data):
        if not state.is_peer():
            return
        print("LAN server discovered:", data)

lan = LanEmulator()
