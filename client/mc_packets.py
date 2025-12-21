import json
from mc_codec import *

def parse_handshake(data):
    buf = Buffer(data)
    buf.read_varint()
    protocol = buf.read_varint()
    addr = buf.read_string()
    port = buf.read_ushort()
    next_state = buf.read_varint()
    return protocol, addr, port, next_state


def is_status_request(data):
    buf = Buffer(data)
    return buf.read_varint() == 0x00


def make_status_response():
    payload = {
        "version": {
            "name": "Minelink v6.7",
            "protocol": 758
        },
        "players": {
            "max": 20,
            "online": 1
        },
        "description": {
            "text": "Minelink LAN Bridge (v6.7)"
        }
    }
    return make_packet(0x00, json.dumps(payload))
