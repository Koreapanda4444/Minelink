import socket
import threading

hosts = {}

def log(msg):
    print(f"[RELAY] {msg}")

def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError
        buf += chunk
    return buf.decode().strip()

def read_varint(sock):
    num = 0
    shift = 0
    while True:
        b = sock.recv(1)
        if not b:
            raise ConnectionError
        val = b[0]
        num |= (val & 0x7F) << shift
        if not (val & 0x80):
            return num
        shift += 7

def read_packet(sock):
    length = read_varint(sock)
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError
        data += chunk
    return data

def write_varint(sock, value):
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            sock.send(bytes([b | 0x80]))
        else:
            sock.send(bytes([b]))
            break

def write_packet(sock, data):
    write_varint(sock, len(data))
    sock.sendall(data)

def pipe_packets(src, dst, tag):
    log(f"packet pipe start: {tag}")
    try:
        while True:
            pkt = read_packet(src)
            write_packet(dst, pkt)
    except Exception as e:
        log(f"packet pipe closed: {tag} ({e})")
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def handle(sock, addr):
    try:
        line = recv_line(sock)
        role, code = line.split()
        log(f"{addr} -> {role} {code}")

        if role == "HOST":
            hosts[code] = sock
            log(f"HOST registered: code={code}")

            while True:
                data = sock.recv(1)
                if not data:
                    break

            log(f"HOST disconnected: code={code}")
            hosts.pop(code, None)
            return

        if role == "JOIN":
            if code not in hosts:
                log(f"JOIN failed: code={code} (no host)")
                sock.close()
                return

            host = hosts.pop(code)
            log(f"JOIN success: code={code}")

            host.sendall(b"PEER_JOINED\n")
            host.sendall(f"{addr[0]}:{addr[1]}\n".encode())

            threading.Thread(
                target=pipe_packets,
                args=(host, sock, f"host->{addr}"),
                daemon=True
            ).start()

            threading.Thread(
                target=pipe_packets,
                args=(sock, host, f"{addr}->host"),
                daemon=True
            ).start()

    except Exception as e:
        log(f"error: {e}")
        try:
            sock.close()
        except:
            pass

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 9000))
    s.listen(50)
    log("relay server started on :9000")

    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()
