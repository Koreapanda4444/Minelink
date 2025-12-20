import socket
import threading

hosts = {}

def pipe(a, b):
    try:
        while True:
            data = a.recv(4096)
            if not data:
                break
            b.sendall(data)
    except:
        pass
    finally:
        try:
            a.close()
        except:
            pass
        try:
            b.close()
        except:
            pass

def handle(sock, addr):
    line = b""
    while not line.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            return
        line += chunk

    role, code = line.decode().strip().split()

    if role == "HOST":
        hosts[code] = sock
        return

    if role == "JOIN":
        if code not in hosts:
            sock.close()
            return

        host = hosts.pop(code)
        host.sendall(f"{addr[0]}:{addr[1]}\n".encode())

        threading.Thread(target=pipe, args=(host, sock), daemon=True).start()
        threading.Thread(target=pipe, args=(sock, host), daemon=True).start()

def main():
    s = socket.socket()
    s.bind(("0.0.0.0", 9000))
    s.listen(10)

    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()
