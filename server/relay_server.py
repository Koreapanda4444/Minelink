import socket
import threading
from sessions import Session

HOST = "0.0.0.0"
PORT = 9000

sessions = {}
lock = threading.Lock()

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        d = sock.recv(1)
        if not d:
            raise ConnectionError
        buf += d
    return buf.decode().strip()

def pipe(a, b, label):
    try:
        while True:
            d = a.recv(4096)
            if not d:
                break
            b.sendall(d)
    except Exception as e:
        print(f"[PIPE] {label} 종료: {e}")
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass

def handle_client(sock, addr):
    try:
        line = recv_line(sock)
        parts = line.split()

        if parts[0] == "HOST":
            code = parts[1]
            with lock:
                sess = Session(code)
                sess.register_host(sock)
                sessions[code] = sess
            sock.sendall(b"HOST_OK\n")
            print(f"[RELAY] HOST 등록: {code}")

        elif parts[0] == "JOIN":
            code = parts[1]
            with lock:
                sess = sessions.get(code)
            if not sess:
                sock.sendall(b"NO_SESSION\n")
                sock.close()
                return

            pid = sess.add_peer(sock)
            sock.sendall(f"JOIN_OK {pid}\n".encode())
            print(f"[RELAY] PEER 참가: {addr} -> {code} (pid={pid})")

            sess.host_ctrl.sendall(f"NEW_PEER {pid}\n".encode())

            host_data, _ = sess.host_ctrl.accept()
            sess.bind_host_peer(pid, host_data)

            threading.Thread(
                target=pipe,
                args=(sock, host_data, f"peer{pid}->{code}"),
                daemon=True
            ).start()

            threading.Thread(
                target=pipe,
                args=(host_data, sock, f"{code}->peer{pid}"),
                daemon=True
            ).start()

    except Exception as e:
        print(f"[RELAY] error: {e}")

def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print(f"[RELAY] 멀티피어 릴레이 시작 :{PORT}")

    while True:
        c, a = s.accept()
        threading.Thread(
            target=handle_client,
            args=(c, a),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()
