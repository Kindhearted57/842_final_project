import threading
def _AllocatorThread():
    return "Hi"

t = threading.Thread(target=_AllocatorThread, args=(),daemon=True)
t.start()

print(t)