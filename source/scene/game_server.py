import socket
import threading

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.clients = []

        # Use self.sock as the instance attribute
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(2)  # max 2 players
        print(f"Server started at {host}:{port}")

    def accept_clients(self):
        print("Waiting for client...")
        client, addr = self.sock.accept()  # blocking call
        print(f"Client connected: {addr}")
        self.clients.append(client)
        # Here you can trigger game start for server
        return client, addr

    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    break
                print("Received:", data.decode())
            except:
                break
        client.close()
