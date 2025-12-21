class Buffer:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, n):
        v = self.data[self.pos:self.pos+n]
        self.pos += n
        return v

    def read_varint(self):
        num = 0
        shift = 0
        while True:
            b = self.read(1)[0]
            num |= (b & 0x7F) << shift
            if not (b & 0x80):
                return num
            shift += 7

    def read_ushort(self):
        b = self.read(2)
        return (b[0] << 8) | b[1]

    def read_string(self):
        length = self.read_varint()
        return self.read(length).decode()


def read_varint(sock):
    num = 0
    shift = 0
    while True:
        b = sock.recv(1)[0]
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            return num
        shift += 7


def write_varint(sock, value):
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            sock.send(bytes([b | 0x80]))
        else:
            sock.send(bytes([b]))
            break


def read_packet(sock):
    length = read_varint(sock)
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))
    return data


def write_packet(sock, data):
    write_varint(sock, len(data))
    sock.sendall(data)


def make_packet(packet_id, payload):
    body = bytes([packet_id]) + payload.encode()
    return body
