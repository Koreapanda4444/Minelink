from state import state
from lan import lan
from network import network

network.on_receive = lan.emit


RED = "\033[31m"
RESET = "\033[0m"

BANNER = f"""
{RED}========================
     Minelink Client
========================{RESET}
"""


def cmd_host():
    print("[*] Host mode selected")
    state.mode = "host"

def cmd_join(args):
    if len(args) != 1:
        print("Usage: !join <code>")
        return
    code = args[0]
    print(f"[*] Joining session {code}")
    state.mode = "peer"
    state.session_code = code

def cmd_status():
    state.print_status()

def cmd_help():
    print("""
Available commands:
  !host               Start host mode
  !join <code>        Join session
  !status             Show status
  !help               Show this help
  !exit               Exit program
""")

def handle_command(raw: str):
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
        print("Exiting...")
        exit(0)
    else:
        print("Unknown command. Type !help")

def main():
    print(BANNER)
    while True:
        try:
            raw = input("Minelink> ").strip()
            handle_command(raw)
        except KeyboardInterrupt:
            print("\nInterrupted")
            break

if __name__ == "__main__":
    main()
