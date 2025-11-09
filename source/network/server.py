# server.py (only slight modification)
import asyncio
import json

clients = []

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    clients.append(writer)

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            msg = json.loads(data.decode().strip())
            print(f"Received: {msg}")

            # Broadcast to other clients except sender
            for c in clients:
                if c != writer:
                    c.write((json.dumps(msg) + "\n").encode())
                    await c.drain()

    except Exception as e:
        print("Error:", e)
    finally:
        print("Client disconnected:", addr)
        clients.remove(writer)
        writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 5555)
    print("Server started on port 5555")
    async with server:
        await server.serve_forever()

asyncio.run(main())
