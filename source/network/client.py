# network/client.py
import asyncio
import json
from threading import Thread

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5555, keyword=None, is_host=None, on_message=None):
        self.host = host
        self.port = port
        self.keyword = keyword
        self.on_message = on_message
        self.writer = None
        self.authorized = False
        self.loop = None
        self.is_host = is_host

    async def _connect(self):
        """Connects to the server and starts listening for messages."""
        self.loop = asyncio.get_event_loop()
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.writer = writer
        print(f"✅ Connected to server at {self.host}:{self.port}")

        # Send keyword immediately for authorization
        if self.keyword:
            self.send({"type": "keyword", "keyword": self.keyword})

        while True:
            try:
                data = await reader.readline()
                if not data:
                    print("⚠️ Disconnected from server.")
                    break

                msg = json.loads(data.decode().strip())
                msg_type = msg.get("type")

                # 🔐 Handle authorization
                if msg_type == "keyword":
                    if msg.get("keyword") == self.keyword:
                        self.authorized = True
                        print("✅ Keyword matched. Authorized!")
                        if self.on_message:
                            self.on_message({"type": "authorized"})
                    else:
                        print("❌ Keyword mismatch.")
                        if self.on_message:
                            self.on_message({"type": "unauthorized"})

                # 🔔 Game start
                elif msg_type == "ready":
                    self.authorized = True
                    print("🎮 Other player ready. Starting game!")
                    if self.on_message:
                        self.on_message({"type": "ready"})

                # 🔄 Game state updates
                elif msg_type == "game_state" and self.authorized:
                    #print("📩 Received: game_state from server")
                    if self.on_message:
                        self.on_message(msg)

                # 🔁 Turn switch sync
                elif msg_type == "turn_update" and self.authorized:
                    print("🔁 Turn switch message received")
                    if self.on_message:
                        self.on_message(msg)

            except Exception as e:
                print("❗ Network error:", e)
                break

    def start(self):
        """Starts the client in a background thread."""
        def run():
            asyncio.run(self._connect())
        Thread(target=run, daemon=True).start()

    def send(self, data):
        """Send a JSON message safely to the server."""
        if not self.writer or not self.loop:
            print("⚠️ Cannot send: not connected yet.")
            return

        try:
            msg = (json.dumps(data) + "\n").encode()
            self.writer.write(msg)
            # ✅ Thread-safe flush to make sure message is sent immediately
            asyncio.run_coroutine_threadsafe(self.writer.drain(), self.loop)
            #print(f"📤 Sent message: {data['type']}")
        except Exception as e:
            print("❌ Send error:", e)
