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
    return buf.decode(errors="ignore").strip()


def pipe(src, dst, label, on_close=None):
    src.settimeout(5.0)
    dst.settimeout(5.0)

    try:
        while True:
            try:
                data = src.recv(4096)
                if not data:
                    break
            except socket.timeout:
                continue

            try:
                dst.sendall(data)
            except:
                break
    except:
        pass
    finally:
        if on_close:
            on_close()

        try:
            src.shutdown(socket.SHUT_RDWR)
            src.close()
        except:
            pass

        try:
            dst.shutdown(socket.SHUT_RDWR)
            dst.close()
        except:
            pass

        print(f"[PIPE] 종료: {label}")


def handle_client(sock, addr):
    sess = None
    pid = None

    try:
        line = recv_line(sock)
        parts = line.split()

        if len(parts) < 2:
            sock.close()
            return

        role, code = parts[0], parts[1]

        if role == "HOST":
            sess = Session(code)
            sess.register_host(sock)

            with lock:
                sessions[code] = sess

            sock.sendall(b"HOST_OK\n")
            print(f"[RELAY] HOST 등록: {code}")

            try:
                while True:
                    sock.recv(1)
            except:
                pass

        elif role == "JOIN":
            with lock:
                sess = sessions.get(code)

            if not sess:
                sock.sendall(b"NO_SESSION\n")
                sock.close()
                return

            pid = sess.add_peer(sock)
            sock.sendall(f"JOIN_OK {pid}\n".encode())
            print(f"[RELAY] PEER 참가: {addr} -> {code} (pid={pid})")

            try:
                sess.host_ctrl.sendall(f"NEW_PEER {pid}\n".encode())
            except:
                sess.remove_peer(pid)
                return

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
                if sessions.get(sess.code) is sess:
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
