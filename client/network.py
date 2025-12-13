import json
import threading
import time
import urllib.request
from state import state
from config import config

class NetworkManager:
    def __init__(self):
        self.running = False
        self.poll_thread = None
        self.peer_thread = None
        self.on_receive = lambda data: None

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

        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.peer_thread = threading.Thread(target=self._peer_sync_loop, daemon=True)

        self.poll_thread.start()
        self.peer_thread.start()

    def disconnect(self):
        self.running = False
        time.sleep(0.2)
        state.network_mode = None

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

    def _poll_loop(self):
        while self.running:
            if not state.session_code:
                time.sleep(0.5)
                continue
            try:
                res = self._post("/relay/pull", {
                    "code": state.session_code
                })
                data = res.get("data")
                if data is not None:
                    self.on_receive(data)
            except:
                pass
            time.sleep(0.05)

    def _peer_sync_loop(self):
        while self.running:
            if not state.session_code:
                time.sleep(1)
                continue
            try:
                res = self._post("/peers", {
                    "code": state.session_code
                })
                state.peers = res.get("peers", [])
            except:
                pass
            time.sleep(2)

network = NetworkManager()
