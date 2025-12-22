import socket
import threading

sessions = {}

def pipe(a, b, name):
    try:
        while True:
            d = a.recv(4096)
            if not d:
                break
            b.sendall(d)
    except Exception as e:
        print(f"[PIPE] {name} 종료:", e)
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
            sessions[code] = {
                "host_ctrl": sock,
                "host_data": {},
                "peers": {}
            }
            sock.sendall(b"HOST_OK\n")
            print(f"[RELAY] HOST 등록: {code}")
            return

        if parts[0] == "JOIN":
            code = parts[1]
            sess = sessions.get(code)
            if not sess:
                sock.close()
                return

            pid = len(sess["peers"]) + 1
            sess["peers"][pid] = None
            sess["host_ctrl"].sendall(f"NEW_PEER {pid}\n".encode())
            sock.sendall(f"JOIN_OK {pid}\n".encode())
            print(f"[RELAY] PEER 참가: {addr} -> {code} (pid={pid})")
            return

        if parts[0] == "DATA":
            pid = int(parts[1])
            for sess in sessions.values():
                if pid in sess["peers"] and sess["peers"][pid] is None:
                    sess["peers"][pid] = sock
                    if pid in sess["host_data"]:
                        start_pipe_pair(sess, pid)
                    return
                if pid in sess["host_data"] and sess["peers"].get(pid) is None:
                    sess["host_data"][pid] = sock
                    if pid in sess["peers"]:
                        start_pipe_pair(sess, pid)
                    return
    except Exception as e:
        print("[RELAY] error:", e)

def start_pipe_pair(sess, pid):
    host = sess["host_data"].get(pid)
    peer = sess["peers"].get(pid)
    if not host or not peer:
        return

    print(f"[RELAY] DATA pipe 연결 (pid={pid})")
    threading.Thread(target=pipe, args=(host, peer, f"h->{pid}"), daemon=True).start()
    threading.Thread(target=pipe, args=(peer, host, f"{pid}->h"), daemon=True).start()

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        d = sock.recv(1)
        if not d:
            raise ConnectionError
        buf += d
    return buf.decode().strip()

def main():
    s = socket.socket()
    s.bind(("0.0.0.0", 9000))
    s.listen()
    print("[RELAY] 멀티피어 릴레이 시작 :9000")

    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()
