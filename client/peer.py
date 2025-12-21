import socket
from config import *
from mc_codec import *
from mc_packets import *
from mc_states import *

def start_peer(code):
    print("[PEER] connecting to relay...")
    relay = socket.socket()
    relay.connect((ORACLE_HOST, ORACLE_PORT))
    relay.sendall(f"JOIN {code}\n".encode())
    print(f"[PEER] sent JOIN request (code={code})")

    listen = socket.socket()
    listen.bind((PEER_BIND_HOST, PEER_BIND_PORT))
    listen.listen(1)
    print(f"[PEER] waiting for minecraft client on {PEER_BIND_PORT}...")

    mc, addr = listen.accept()
    print(f"[PEER] minecraft client connected from {addr}")

    state = HANDSHAKE

    while True:
        pkt = read_packet(mc)
        print(f"[PEER] received packet ({len(pkt)} bytes)")

        if state == HANDSHAKE:
            protocol, addr, port, next_state = parse_handshake(pkt)
            print(f"[PEER] handshake protocol={protocol} next_state={next_state}")
            state = next_state

            if state == STATUS:
                print("[PEER] entering STATUS state")
                continue

            write_packet(relay, pkt)
            print("[PEER] forwarded handshake to relay")
            break

        if state == STATUS:
            if is_status_request(pkt):
                print("[PEER] STATUS request received")
                resp = make_status_response()
                write_packet(mc, resp)
                print("[PEER] STATUS response sent")
                continue
