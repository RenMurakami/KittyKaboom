from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading
import time

from scene.game_client import GameClient
from scene.game_server import GameServer


class OnlineSetup(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.server = None
        self.client = None
        self.server_thread = None

        # Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.info_label = Label(text="Setup online match", size_hint=(1, 0.2))
        layout.add_widget(self.info_label)

        self.room_input = TextInput(
            hint_text="Enter room name or server IP",
            size_hint=(1, 0.2)
        )
        layout.add_widget(self.room_input)

        join_btn = Button(text="Join Room", size_hint=(1, 0.2))
        join_btn.bind(on_release=self.join_room)
        layout.add_widget(join_btn)

        host_btn = Button(text="Host Room", size_hint=(1, 0.2))
        host_btn.bind(on_release=self.host_room)
        layout.add_widget(host_btn)

        back_btn = Button(text="Back", size_hint=(1, 0.2))
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def join_room(self, instance):
        room_ip = self.room_input.text.strip()
        if not room_ip:
            self.info_label.text = "Enter server IP!"
            return

        self.info_label.text = f"Connecting to {room_ip}..."
        threading.Thread(target=self._join_thread, args=(room_ip,), daemon=True).start()

    def _join_thread(self, room_ip):
        try:
            self.client = GameClient(room_ip)
            print("Connected to server, starting game (client side)")
            Clock.schedule_once(lambda dt: self._switch_to_game(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_label(f"Failed to join: {e}"), 0)

    def host_room(self, instance):
        port = 12345
        try:
            self.server = GameServer(port=port)
            # Start a background thread to wait for clients
            threading.Thread(target=self._wait_for_client, daemon=True).start()
            print(f"Hosting game on port {port}")
        except Exception as e:
            print("Failed to host:", e)

    def _host_thread(self, port):
        try:
            self.server = GameServer(port=port)
            Clock.schedule_once(lambda dt: self._update_label(f"Waiting for client on port {port}..."), 0)
            self.server.accept_clients()  # blocks until client connects

            # When client connects, update UI on main thread
            Clock.schedule_once(lambda dt: self._switch_to_game(), 0)

            print("Client connected, starting game (server side)")
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_label(f"Failed to host: {e}"), 0)

    def _update_label(self, text):
        self.info_label.text = text
        
    def _wait_for_client(self):
        self.server.sock.listen(1)
        client, addr = self.server.sock.accept()
        print(f"Client connected: {addr}")
        self.server.client = client
        # switch screen on main thread
        Clock.schedule_once(lambda dt: self._switch_to_game(), 0)

    def _switch_to_game(self):
        self.info_label.text = "Connected!"
        self.manager.current = "stage1_1"  # Switch to your game screen

    def go_back(self, instance):
        self.manager.current = "match_select"
