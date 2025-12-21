import socket
import threading

def pipe(a, b, tag=""):
    try:
        while True:
            data = a.recv(4096)
            if not data:
                break
            b.sendall(data)
    except:
        pass
    finally:
        try: a.close()
        except: pass
        try: b.close()
        except: pass
