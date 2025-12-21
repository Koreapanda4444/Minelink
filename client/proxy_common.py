import threading

def pipe(a, b, name="PIPE"):
    try:
        while True:
            d = a.recv(4096)
            if not d:
                break
            b.sendall(d)
    except Exception as e:
        print(f"[{name}] 종료:", e)
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass

def start_pipe(a, b, label):
    threading.Thread(
        target=pipe,
        args=(a, b, label),
        daemon=True
    ).start()
