import json
import urllib.request
from state import state
from config import config

class OracleClient:
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

    def create_session(self):
        res = self._post("/create", {})
        state.mode = "host"
        state.session_code = res.get("code")
        state.oracle_connected = True
        print("Session created:", state.session_code)

    def join_session(self, code):
        res = self._post("/join", {"code": code})
        if not res.get("ok"):
            print("Join failed")
            return
        state.mode = "peer"
        state.session_code = code
        state.oracle_connected = True
        print("Joined session:", code)

oracle = OracleClient()
