from state import state
from oracle import oracle
from network import network
from lan import lan

RED = "\033[31m"
RESET = "\033[0m"

BANNER = f"""
{RED}========================
     Minelink Client
========================{RESET}
"""

def cmd_host():
    oracle.create_session()
    network.connect()
    lan.start_sniff()

def cmd_join(args):
    if len(args) != 1:
        print("Usage: !join <code>")
        return
    oracle.join_session(args[0])
    network.connect()

def cmd_status():
    print("====== STATUS ======")
    print("Mode          :", state.mode)
    print("Network Mode  :", state.network_mode)
    print("Peers         :", len(state.peers))
    print("====================")

def cmd_help():
    print("""
!host
!join <code>
!status
!help
!exit
""")

def handle_command(raw):
    if not raw:
        return

    parts = raw.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "!host":
        cmd_host()
    elif cmd == "!join":
        cmd_join(args)
    elif cmd == "!status":
        cmd_status()
    elif cmd == "!help":
        cmd_help()
    elif cmd == "!exit":
        network.disconnect()
        exit(0)
    else:
        print("Unknown command")

def main():
    network.on_receive = lan.emit
    print(BANNER)
    while True:
        try:
            raw = input("Minelink> ").strip()
            handle_command(raw)
        except KeyboardInterrupt:
            network.disconnect()
            break

if __name__ == "__main__":
    main()
