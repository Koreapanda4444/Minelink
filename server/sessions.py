import threading
import socket


class Session:
    def __init__(self, code):
        self.code = code
        self.host_ctrl = None
        self.peers = {}
        self.host_peers = {}
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
            ps = self.peers.pop(pid, None)
            hs = self.host_peers.pop(pid, None)

        for s in (ps, hs):
            try:
                if s:
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
            except:
                pass

    def close_all(self):
        with self.lock:
            pids = list(self.peers.keys())

        for pid in pids:
            self.remove_peer(pid)

        try:
            if self.host_ctrl:
                self.host_ctrl.shutdown(socket.SHUT_RDWR)
                self.host_ctrl.close()
        except:
            pass
