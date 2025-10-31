import socket
import threading
import json
import time

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(2)
        print(f"[SERVER] Running on {self.host}:{self.port}")

        # Initialize game state
        game_state = {
            "tanks": [
                {"x": 100, "y": 100, "owner": "host"},   # tank 1
                {"x": 200, "y": 100, "owner": "client"}  # tank 2
            ]
        }


        # Start game loop
        threading.Thread(target=self.game_loop, daemon=True).start()

    def accept_client(self):
        """Blocking call to accept a single client."""
        client_sock, addr = self.sock.accept()
        print(f"[SERVER] Client connected from {addr}")
        self.clients.append(client_sock)
        return client_sock

    def broadcast(self, data):
        msg = json.dumps(data).encode()
        for c in self.clients:
            try:
                c.sendall(msg)
            except:
                self.clients.remove(c)

    def game_loop(self):
        while self.running:
            self.broadcast(self.game_state)
            time.sleep(0.05)

                
    def handle_client(self, client):
        while self.running and client:
            try:
                msg = client.recv(1024).decode()
                if not msg:
                    break
            except (OSError, ConnectionResetError):
                break
        if client:
            client.close()
            if client in self.clients:
                self.clients.remove(client)
