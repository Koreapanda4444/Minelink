from host import start_host
from peer import start_peer

BANNER = """
========================================
  Minelink - Minecraft LAN Linker
========================================
!host <CODE>     : Host mode
!join <CODE>     : Peer mode
!exit            : Exit
========================================
"""

def main():
    print(BANNER)

    while True:
        cmd = input("> ").strip()
        if cmd.startswith("!host "):
            start_host(cmd.split()[1])
        elif cmd.startswith("!join "):
            start_peer(cmd.split()[1])
        elif cmd == "!exit":
            break

if __name__ == "__main__":
    main()
