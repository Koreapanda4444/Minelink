import threading
from mc_codec import read_packet, write_packet


class ProxyConnection:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.running = True

    def pipe(self, src, dst, hook=None):
        try:
            while self.running:
                packet = read_packet(src)
                if hook:
                    hook(packet)
                write_packet(dst, packet)
        except Exception:
            self.running = False

    def start(self, hook_a=None, hook_b=None):
        t1 = threading.Thread(
            target=self.pipe, args=(self.a, self.b, hook_a), daemon=True
        )
        t2 = threading.Thread(
            target=self.pipe, args=(self.b, self.a, hook_b), daemon=True
        )
        t1.start()
        t2.start()
        t1.join()
        t2.join()
