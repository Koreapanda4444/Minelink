import json
from mc_codec import read_varint, write_varint

def parse_handshake(data):
    i = 0
    pid, s = _read_varint(data, i)
    proto, s = _read_varint(data, s)
    host_len, s = _read_varint(data, s)
    host = data[s:s+host_len].decode()
    s += host_len
    port = int.from_bytes(data[s:s+2], "big")
    s += 2
    next_state, _ = _read_varint(data, s)
    return proto, host, port, next_state

def status_response():
    payload = {
        "version": {"name": "Minelink", "protocol": 47},
        "players": {"max": 1, "online": 0},
        "description": {"text": "Minelink v6.6"}
    }
    js = json.dumps(payload).encode()
    return write_varint(0x00) + write_varint(len(js)) + js

def pong(payload):
    return write_varint(0x01) + payload

def _read_varint(buf, i):
    num = 0
    shift = 0
    while True:
        b = buf[i]
        i += 1
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return num, i
