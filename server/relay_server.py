import socket
import threading

hosts = {}

def pipe(a, b):
    try:
        while True:
            d = a.recv(4096)
            if not d:
                break
            b.sendall(d)
    except:
        pass
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass

def handle(c, addr):
    try:
        line = b""
        while not line.endswith(b"\n"):
            line += c.recv(1)

        cmd = line.decode().strip().split()
        if cmd[0] == "HOST":
            code = cmd[1]
            hosts[code] = c
            print("[RELAY] HOST", code)

        elif cmd[0] == "JOIN":
            code = cmd[1]
            if code not in hosts:
                c.sendall(b"NO_HOST\n")
                c.close()
                return

            host = hosts[code]
            c.sendall(b"JOIN_OK\n")

            host.sendall(b"PEER_JOINED\n")
            host.sendall(f"{addr[0]}:{addr[1]}\n".encode())

            threading.Thread(target=pipe, args=(host, c), daemon=True).start()
            threading.Thread(target=pipe, args=(c, host), daemon=True).start()

    except Exception as e:
        print("[RELAY] error:", e)

def main():
    s = socket.socket()
    s.bind(("0.0.0.0", 9000))
    s.listen(5)
    print("[RELAY] started")

    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()
