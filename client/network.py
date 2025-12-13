import json
import threading
import time
import urllib.request
import socket
from state import state
from config import config

RELAY_CHUNK = 4096

class NetworkManager:
    def __init__(self):
        self.running = False

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
        self.running = True
        state.network_mode = "relay"
        threading.Thread(target=self._poll, daemon=True).start()

    def send(self, data):
        if not state.session_code:
            return
        self._post("/relay/push", {
            "code": state.session_code,
            "data": data
        })

    def _poll(self):
        while self.running:
            if not state.session_code:
                time.sleep(1)
                continue
            res = self._post("/relay/pull", {
                "code": state.session_code
            })
            data = res.get("data")
            if data:
                self.on_receive(data)
            time.sleep(0.01)

    def on_receive(self, data):
        pass

network = NetworkManager()
