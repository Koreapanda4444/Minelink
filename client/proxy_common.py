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
            try:
                src.close()
            except:
                pass
            try:
                dst.close()
            except:
                pass

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
