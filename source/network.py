import socket
import threading

class GameNetwork:
    def __init__(self, conn):
        self.conn = conn
        self.lock = threading.Lock()

    def send(self, message: str):
        try:
            with self.lock:
                self.conn.sendall((message + "\n").encode())
        except Exception as e:
            print("Send failed:", e)

    def recv(self):
        try:
            data = self.conn.recv(1024)
            if not data:
                return None
            return data.decode().strip()
        except:
            return None
