import threading

class Session:
    def __init__(self, code):
        self.code = code
        self.host_ctrl = None
        self.host_peers = {}
        self.peers = {}
        self.next_peer_id = 1
        self.lock = threading.Lock()

    def register_host(self, sock):
        self.host_ctrl = sock

    def add_peer(self, peer_sock):
        with self.lock:
            pid = self.next_peer_id
            self.next_peer_id += 1
            self.peers[pid] = peer_sock
            return pid

    def bind_host_peer(self, pid, host_sock):
        with self.lock:
            self.host_peers[pid] = host_sock

    def remove_peer(self, pid):
        with self.lock:
            self.peers.pop(pid, None)
            self.host_peers.pop(pid, None)
