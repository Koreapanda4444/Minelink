class State:
    def __init__(self):
        self.mode = None
        self.session_code = None
        self.network_mode = None
        self.peers = []

    def print_status(self):
        print("Mode:", self.mode)
        print("Session:", self.session_code)
        print("Network:", self.network_mode)
        print("Peers:", len(self.peers))

state = State()
