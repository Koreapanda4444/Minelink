from state import state

class OracleClient:
    def create_session(self):
        state.mode = "host"
        state.session_code = "XXXXXX"
        print("Session created:", state.session_code)

    def join_session(self, code):
        state.mode = "peer"
        state.session_code = code
        print("Joined session:", code)

oracle = OracleClient()
