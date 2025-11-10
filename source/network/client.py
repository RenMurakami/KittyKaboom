# network/client.py
import asyncio
import json
from threading import Thread

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555, keyword=None, on_message=None):
        self.host = host
        self.port = port
        self.keyword = keyword
        self.on_message = on_message
        self.writer = None
        self.authorized = False

    async def _connect(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.writer = writer
        print("Connected to server")

        # Send keyword immediately
        if self.keyword:
            self.send({"type": "keyword", "keyword": self.keyword})

        while True:
            try:
                data = await reader.readline()
                if not data:
                    break
                msg = json.loads(data.decode())

                if msg.get("type") == "keyword":
                    if msg.get("keyword") == self.keyword:
                        self.authorized = True
                        print("Keyword matched. Authorized!")
                        if self.on_message:
                            self.on_message({"type": "authorized"})
                    else:
                        print("Keyword mismatch")
                        if self.on_message:
                            self.on_message({"type": "unauthorized"})
                elif self.authorized and self.on_message:
                    self.on_message(msg)
                    
                if msg.get("type") == "ready":
                    self.authorized = True
                    print("Keyword matched. Authorized!")
                    if self.on_message:
                        self.on_message({"type": "ready"})
                    

            except Exception as e:
                print("Network error:", e)
                break

    def start(self):
        Thread(target=lambda: asyncio.run(self._connect()), daemon=True).start()

    def send(self, data):
        if not self.writer:
            return
        try:
            self.writer.write((json.dumps(data) + "\n").encode())
        except Exception as e:
            print("Send error:", e)
