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


def parse_status_response(packet):
    buf = BytesIO(packet)
    packet_id = read_varint_buf(buf)
    if packet_id != 0x00:
        return None
    json_len = read_varint_buf(buf)
    return buf.read(json_len).decode()


def parse_disconnect(packet):
    buf = BytesIO(packet)
    packet_id = read_varint_buf(buf)
    if packet_id != 0x00:
        return None
    msg_len = read_varint_buf(buf)
    return buf.read(msg_len).decode()
