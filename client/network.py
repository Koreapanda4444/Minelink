from state import state

class NetworkManager:
    def connect(self):
        state.network_mode = "relay"
        print("Relay connection")

network = NetworkManager()
