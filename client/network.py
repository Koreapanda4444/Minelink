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
        self._close_tcp()

    def _close_tcp(self):
        try:
            if self.tcp_socket:
                self.tcp_socket.shutdown(socket.SHUT_RDWR)
                self.tcp_socket.close()
        except:
            pass
        self.tcp_socket = None

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
                pkt = res.get("data")
                if pkt:
                    self._handle_packet(pkt)
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

        if not self.tcp_socket:
            return

        try:
            data = bytes.fromhex(pkt["data"])
            self.tcp_socket.sendall(data)
        except:
            self._close_tcp()

    def _tcp_peer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", MC_PORT))
        server.listen(1)

        while self.running:
            try:
                conn, _ = server.accept()
                self.tcp_socket = conn
                conn.setblocking(False)

                while self.running:
                    r, _, _ = select.select([conn], [], [], 0.1)
                    if conn in r:
                        data = conn.recv(4096)
                        if not data:
                            break
                        self.send({
                            "type": "tcp",
                            "data": data.hex()
                        })
            except:
                pass
            finally:
                self._close_tcp()

        server.close()

    def _tcp_host(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", MC_PORT))
                s.setblocking(False)
                self.tcp_socket = s

                while self.running:
                    r, _, _ = select.select([s], [], [], 0.1)
                    if s in r:
                        data = s.recv(4096)
                        if not data:
                            break
                        self.send({
                            "type": "tcp",
                            "data": data.hex()
                        })
            except:
                time.sleep(1)
            finally:
                self._close_tcp()

network = NetworkManager()
