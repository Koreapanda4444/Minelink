import json
import threading
import time
import urllib.request
import socket
import select
from state import state
from config import config

MC_PORT = 25565

class NetworkManager:
    def __init__(self):
        self.running = False
        self.on_receive = lambda data: None
        self.tcp_socket = None

    def _post(self, path, data):
        url = f"http://{config.oracle_host}:{config.oracle_port}{path}"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as res:
            return json.loads(res.read().decode())

    def connect(self):
        if self.running:
            return
        self.running = True
        state.network_mode = "relay"
        threading.Thread(target=self._relay_poll, daemon=True).start()
        threading.Thread(target=self._peer_sync, daemon=True).start()

        if state.is_peer():
            threading.Thread(target=self._tcp_peer, daemon=True).start()
        if state.is_host():
            threading.Thread(target=self._tcp_host, daemon=True).start()

    def disconnect(self):
        self.running = False
        state.network_mode = None
        try:
            if self.tcp_socket:
                self.tcp_socket.close()
        except:
            pass

    def send(self, data):
        if not self.running or not state.session_code:
            return
        try:
            self._post("/relay/push", {
                "code": state.session_code,
                "data": data
            })
        except:
            pass

    def _relay_poll(self):
        while self.running:
            try:
                res = self._post("/relay/pull", {
                    "code": state.session_code
                })
                data = res.get("data")
                if data:
                    self._handle_packet(data)
            except:
                pass
            time.sleep(0.05)

    def _peer_sync(self):
        while self.running:
            try:
                res = self._post("/peers", {
                    "code": state.session_code
                })
                state.peers = res.get("peers", [])
            except:
                pass
            time.sleep(2)

    def _handle_packet(self, pkt):
        if pkt.get("type") != "tcp":
            self.on_receive(pkt)
            return

        if pkt.get("dir") == "host_to_peer" and state.is_peer():
            try:
                data = bytes.fromhex(pkt["data"])
                if self.tcp_socket:
                    self.tcp_socket.sendall(data)
            except:
                pass

        if pkt.get("dir") == "peer_to_host" and state.is_host():
            try:
                data = bytes.fromhex(pkt["data"])
                if self.tcp_socket:
                    self.tcp_socket.sendall(data)
            except:
                pass

    def _tcp_peer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", MC_PORT))
        s.listen(1)
        self.tcp_socket, _ = s.accept()
        self.tcp_socket.setblocking(False)

        while self.running:
            r, _, _ = select.select([self.tcp_socket], [], [], 0.05)
            if self.tcp_socket in r:
                data = self.tcp_socket.recv(4096)
                if not data:
                    break
                self.send({
                    "type": "tcp",
                    "dir": "peer_to_host",
                    "data": data.hex()
                })
        s.close()

    def _tcp_host(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect(("127.0.0.1", MC_PORT))
        self.tcp_socket.setblocking(False)

        while self.running:
            r, _, _ = select.select([self.tcp_socket], [], [], 0.05)
            if self.tcp_socket in r:
                data = self.tcp_socket.recv(4096)
                if not data:
                    break
                self.send({
                    "type": "tcp",
                    "dir": "host_to_peer",
                    "data": data.hex()
                })
        self.tcp_socket.close()

network = NetworkManager()
