import socket
import threading


def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    finally:
        src.close()
        dst.close()


server = socket.socket()
server.bind(("0.0.0.0", 9000))
server.listen()

print("[relay] listening on :9000")

while True:
    a, _ = server.accept()
    b, _ = server.accept()

    threading.Thread(target=pipe, args=(a, b), daemon=True).start()
    threading.Thread(target=pipe, args=(b, a), daemon=True).start()
