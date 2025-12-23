import socket
import threading
from proxy_common import pipe
from config import *

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        d = sock.recv(1)
        if not d:
            raise ConnectionError("control channel closed")
        buf += d
    return buf.decode().strip()

def handle_peer(pid, relay_host, relay_port):
    print(f"[HOST] peer {pid} 데이터 채널 연결 중")

    data = socket.socket()
    data.connect((relay_host, relay_port))

    mc = socket.socket()
    mc.connect((MC_SERVER_HOST, MC_SERVER_PORT))

    print(f"[HOST] peer {pid} mc 연결 완료")

    def cleanup():
        try: data.close()
        except: pass
        try: mc.close()
        except: pass
        print(f"[HOST] peer {pid} 세션 종료")

    threading.Thread(
        target=lambda: (pipe(data, mc, f"relay{pid}->mc"), cleanup()),
        daemon=True
    ).start()

    threading.Thread(
        target=lambda: (pipe(mc, data, f"mc->relay{pid}"), cleanup()),
        daemon=True
    ).start()

def start_host(code):
    ctrl = socket.socket()
    ctrl.connect((ORACLE_HOST, ORACLE_PORT))
    ctrl.sendall(f"HOST {code}\n".encode())
    print(f"[HOST] HOST 등록 완료: {code}")
    print("[HOST] peer 대기 중...")

    relay_host, relay_port = ctrl.getpeername()

    while True:
        try:
            line = recv_line(ctrl)
        except Exception as e:
            print(f"[HOST] control 종료: {e}")
            break

        parts = line.split()

        if parts[0] == "HOST_OK":
            print("[HOST] 릴레이 등록 확인 완료")
            continue

        if parts[0] == "NEW_PEER":
            pid = parts[1]
            print(f"[HOST] 신규 PEER 접속: {pid}")
            threading.Thread(
                target=handle_peer,
                args=(pid, relay_host, relay_port),
                daemon=True
            ).start()
            continue

        print(f"[HOST] 알 수 없는 control 메시지: {line}")
