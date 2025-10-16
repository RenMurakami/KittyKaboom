import socket

class GameClient:
    def __init__(self, host, port=12345):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        print(f"Connected to server {host}:{port}")

    def send(self, msg):
        self.client.send(msg.encode())

    def receive(self):
        return self.client.recv(1024).decode()
