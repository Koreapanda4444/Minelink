from io import BytesIO


def read_varint_buf(buf):
    num = 0
    shift = 0
    while True:
        b = buf.read(1)[0]
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            return num
        shift += 7


def parse_packet_id(packet):
    buf = BytesIO(packet)
    return read_varint_buf(buf)


def is_login_success(packet):
    buf = BytesIO(packet)
    pid = read_varint_buf(buf)
    return pid == 0x02
