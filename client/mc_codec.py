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
