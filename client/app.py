from peer import start_peer

BANNER = r"""
========================================
  Minelink - Minecraft LAN Linker
========================================
!host            : Host mode
!join <CODE>     : Peer mode
!status          : Show status
!exit            : Exit
========================================
"""


def print_banner():
    print(BANNER)


def repl():
    print_banner()

    while True:
        try:
            cmd = input("minelink> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd == "!host":
            continue

        if cmd.startswith("!join"):
            parts = cmd.split()
            if len(parts) != 2:
                continue

            print("[INFO] starting peer mode")
            start_peer()
            continue

        if cmd == "!status":
            print("[STATUS]")
            print("  Mode        : NONE")
            print("  Peers       : 0")
            continue

        if cmd == "!exit":
            break


if __name__ == "__main__":
    repl()
