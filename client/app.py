from state import state
from oracle import oracle
from lan import lan
from network import network
from config import config

def handle_command(cmd: str):
    if cmd == "!host":
        oracle.create_session()
        lan.start_sniff()
    elif cmd.startswith("!join"):
        parts = cmd.split()
        if len(parts) == 2:
            oracle.join_session(parts[1])
            network.connect()
    elif cmd == "!status":
        state.print_status()
    elif cmd == "!exit":
        exit(0)
    else:
        print("Unknown command")

def main():
    print("Minelink v4")
    while True:
        cmd = input("Minelink> ").strip()
        handle_command(cmd)

if __name__ == "__main__":
    main()
