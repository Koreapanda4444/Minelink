class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.mode = None
        self.session_code = None
        self.nickname = None
        self.oracle_connected = False
        self.network_mode = None
        self.peers = []

    def is_host(self):
        return self.mode == "host"

    def is_peer(self):
        return self.mode == "peer"

    def print_status(self):
        print("====== STATUS ======")
        print("Mode          :", self.mode)
        print("Session Code  :", self.session_code)
        print("Network Mode  :", self.network_mode)
        print("Oracle Conn   :", self.oracle_connected)
        print("Peers         :", len(self.peers))
        print("====================")

state = State()
