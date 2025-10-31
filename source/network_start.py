import socket
import threading
from game_system import NetworkLink, BaseStage

def start_host(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(1)
    print("🔵 Waiting for client to connect...")
    conn, addr = s.accept()
    print(f"✅ Client connected from {addr}")
    return NetworkLink(conn)

def start_client(host_ip="127.0.0.1", port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_ip, port))
    print("🟢 Connected to host")
    return (s)
