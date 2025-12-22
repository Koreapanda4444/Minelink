import socket
import threading

sessions = {}
pid_map = {}
next_pid = 1

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
    global next_pid
    try:
        line = recv_line(sock)
        parts = line.split()
        if not parts:
            sock.close()
            return

        cmd = parts[0]

        if cmd == "HOST":
            code = parts[1]
            if code in sessions:
                sock.sendall(b"HOST_FAIL exists\n")
                sock.close()
                return

            sessions[code] = {
                "host_ctrl": sock,
                "pid_sockets": {}
            }
            sock.sendall(b"HOST_OK\n")
            print(f"[RELAY] HOST 등록: {code}")
            return

        if cmd == "JOIN":
            code = parts[1]
            sess = sessions.get(code)
            if not sess:
                sock.sendall(b"JOIN_FAIL no_host\n")
                sock.close()
                return

            pid = next_pid
            next_pid += 1

            sess["pid_sockets"][pid] = []
            pid_map[pid] = sess

            try:
                sess["host_ctrl"].sendall(f"NEW_PEER {pid}\n".encode())
            except Exception as e:
                print(f"[RELAY] NEW_PEER 전송 실패: {e}")
                sock.sendall(b"JOIN_FAIL host_down\n")
                sock.close()
                return

            sock.sendall(f"JOIN_OK {pid}\n".encode())
            print(f"[RELAY] PEER 참가: {addr} -> {code} (pid={pid})")
            return

        if cmd == "DATA":
            pid = int(parts[1])
            sess = pid_map.get(pid)
            if not sess:
                sock.close()
                return

            slots = sess["pid_sockets"].setdefault(pid, [])
            if len(slots) >= 2:
                sock.close()
                return

            slots.append(sock)
            if len(slots) == 2:
                start_pipe_pair(slots[0], slots[1], pid)
            return

    except Exception as e:
        print("[RELAY] error:", e)

def start_pipe_pair(a, b, pid):
    print(f"[RELAY] DATA pipe 연결 (pid={pid})")
    threading.Thread(target=pipe, args=(a, b, f"{pid}:A->B"), daemon=True).start()
    threading.Thread(target=pipe, args=(b, a, f"{pid}:B->A"), daemon=True).start()

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
