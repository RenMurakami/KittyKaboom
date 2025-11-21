# server.py
import asyncio
import json

clients = []
turn_index = 0  # Tracks whose turn it is


async def broadcast(message, exclude_writer=None):
    """Send a message to all connected clients except the one specified."""
    for c in clients:
        if c != exclude_writer:
            try:
                c.write((json.dumps(message) + "\n").encode())
                await c.drain()
            except Exception as e:
                print("Error sending to client:", e)


async def send_turn_update():
    """Server-authoritative turn update."""
    global turn_index
    if not clients:
        return
    message = {
        "type": "turn_update",
        "turn_index": turn_index
    }
    await broadcast(message)
    print(f"Server: Turn switched. Now it's player {turn_index}'s turn.")


async def handle_client(reader, writer):
    global turn_index

    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    clients.append(writer)

    # Send current turn to the new client
    try:
        writer.write((json.dumps({"type": "turn_update", "turn_index": turn_index}) + "\n").encode())
        await writer.drain()
    except Exception as e:
        print("Error sending initial turn:", e)

    await broadcast({"type": "info", "message": "New player joined"}, exclude_writer=writer)

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            msg = json.loads(data.decode().strip())

            msg_type = msg.get("type")
            print(f"msg_type={msg_type}")

            # Only broadcast regular gameplay messages (e.g., moves, chat, actions)
            if msg_type not in ("turn_update",):
                await broadcast(msg, exclude_writer=writer)

            # Turn switch command should **only be triggered by the server**.
            # Here we check a "request_turn_end" message from client to trigger server-side turn update
            if msg_type == "turn_update":
                # Move to next player's turn
                if clients:
                    turn_index = (turn_index + 1) % len(clients)
                    await send_turn_update()

    except Exception as e:
        print("Error:", e)
    finally:
        print("Client disconnected:", addr)
        if writer in clients:
            idx = clients.index(writer)
            clients.remove(writer)

            # Adjust turn index if needed
            if idx <= turn_index and turn_index > 0:
                turn_index -= 1
            turn_index %= max(len(clients), 1)

            await broadcast({
                "type": "player_left",
                "turn_index": turn_index,
                "message": f"Player {idx} left. Next turn: {turn_index}"
            })

        writer.close()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 5555)
    print("Server started on port 5555")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
