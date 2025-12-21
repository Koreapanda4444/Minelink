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

def pipe(a, b, label, on_close=None):
    try:
        while True:
            d = a.recv(4096)
            if not d:
                break
            b.sendall(d)
    except:
        pass
    finally:
        if on_close:
            on_close()
        try: a.close()
        except: pass
        try: b.close()
        except: pass
        print(f"[PIPE] 종료: {label}")

def handle_client(sock, addr):
    sess = None
    pid = None
    try:
        line = recv_line(sock)
        parts = line.split()

        if parts[0] == "HOST":
            code = parts[1]
            sess = Session(code)
            sess.register_host(sock)
            with lock:
                sessions[code] = sess
            sock.sendall(b"HOST_OK\n")
            print(f"[RELAY] HOST 등록: {code}")

            sock.recv(1)

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
                args=(
                    sock,
                    host_data,
                    f"peer{pid}->{code}",
                    lambda: sess.remove_peer(pid)
                ),
                daemon=True
            ).start()

            threading.Thread(
                target=pipe,
                args=(
                    host_data,
                    sock,
                    f"{code}->peer{pid}",
                    None
                ),
                daemon=True
            ).start()

    except Exception as e:
        print(f"[RELAY] error: {e}")

    finally:
        if sess and pid is None:
            with lock:
                if sessions.get(sess.code) == sess:
                    del sessions[sess.code]
            sess.close_all()
            print(f"[RELAY] HOST 종료: {sess.code}")

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
