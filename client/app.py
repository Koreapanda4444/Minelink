from host import start_host
from peer import start_peer

BANNER = r"""
========================================
  Minelink - Minecraft LAN Linker
========================================
!host <CODE>     : Host mode
!join <CODE>     : Peer mode
!exit            : Exit
========================================
"""

def repl():
    print(BANNER)

    while True:
        try:
            cmd = input("minelink> ").strip()
        except:
            break

        if not cmd:
            continue

        parts = cmd.split()

        if parts[0] == "!host" and len(parts) == 2:
            print(f"[INFO] Host started (code={parts[1]})")
            start_host(parts[1])
            continue

        if parts[0] == "!join" and len(parts) == 2:
            print("[INFO] starting peer mode")
            start_peer(parts[1])
            continue

        if parts[0] == "!exit":
            break

if __name__ == "__main__":
    repl()
