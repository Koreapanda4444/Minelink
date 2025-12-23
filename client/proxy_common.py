import threading

def pipe(a, b, name="PIPE"):
    try:
        while True:
            data = a.recv(4096)
            if not data:
                break
            b.sendall(data)
    except Exception as e:
        print(f"[{name}] 종료:", e)
    finally:
        pass


def start_pipe(a, b, label):
    threading.Thread(
        target=pipe,
        args=(a, b, label),
        daemon=True
    ).start()
