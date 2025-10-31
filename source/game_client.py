# game_client.py
import socket
import threading
import json

class GameClient:
    def __init__(self, host, port=12345, on_update=None):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print(f"[CLIENT] Connected to server {host}:{port}")
        self.running = True
        self.on_update = on_update
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while self.running and self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                game_state = json.loads(data.decode())
                if self.on_update:
                    self.on_update(game_state)
            except (OSError, ConnectionResetError):
                break
        if self.sock:
            self.sock.close()
            self.sock = None




    def send(self, message):
        self.sock.sendall(message.encode())

    def send_move(self, dx, dy):
        if not self.sock:
            return
        command = {"action":"move", "tank_id":self.tank_id, "dx":dx, "dy":dy}
        self.sock.sendall(json.dumps(command).encode())

