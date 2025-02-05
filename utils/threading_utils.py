import threading

def start_thread(target):
    threading.Thread(target=target, daemon=True).start()