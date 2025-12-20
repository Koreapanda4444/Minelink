from io import BytesIO
from mc_states import STATUS, LOGIN


def read_varint_buf(buf):
    num = 0
    shift = 0
    while True:
        b = buf.read(1)[0]
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            return num
        shift += 7


def parse_handshake(packet):
    buf = BytesIO(packet)

    packet_id = buf.read(1)[0]
    if packet_id != 0x00:
        return None

    protocol_version = read_varint_buf(buf)

    addr_len = read_varint_buf(buf)
    server_addr = buf.read(addr_len).decode()

    server_port = int.from_bytes(buf.read(2), "big")

    next_state = read_varint_buf(buf)

    return {
        "protocol": protocol_version,
        "address": server_addr,
        "port": server_port,
        "next_state": next_state
    }
