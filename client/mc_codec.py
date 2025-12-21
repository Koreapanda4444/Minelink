import struct

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
            break
        shift += 7
    return num

def write_varint(n):
    out = b""
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b | 0x80])
        else:
            out += bytes([b])
            break
    return out

def read_packet(sock):
    length = read_varint(sock)
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))
    return data

def write_packet(sock, data):
    sock.sendall(write_varint(len(data)) + data)
