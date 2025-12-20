import threading
from mc_codec import read_packet, write_packet

class ProxyConnection:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.running = True

    def pipe(self, src, dst):
        try:
            while self.running:
                data = read_packet(src)
                write_packet(dst, data)
        except:
            self.running = False
            try:
                src.close()
            except:
                pass
            try:
                dst.close()
            except:
                pass

    def start(self):
        threading.Thread(target=self.pipe, args=(self.a, self.b), daemon=True).start()
        threading.Thread(target=self.pipe, args=(self.b, self.a), daemon=True).start()
