import threading
import socket
from mc_codec import read_packet, write_packet


class ProxyConnection:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.running = True

        self.a.settimeout(5)
        self.b.settimeout(5)

    def shutdown(self):
        self.running = False
        try:
            self.a.close()
        except:
            pass
        try:
            self.b.close()
        except:
            pass

    def pipe(self, src, dst, hook=None):
        try:
            while self.running:
                packet = read_packet(src)
                if hook:
                    hook(packet)
                write_packet(dst, packet)
        except Exception:
            self.shutdown()

    def start(self, hook_a=None, hook_b=None):
        threading.Thread(
            target=self.pipe,
            args=(self.a, self.b, hook_a),
            daemon=True
        ).start()

        threading.Thread(
            target=self.pipe,
            args=(self.b, self.a, hook_b),
            daemon=True
        ).start()
