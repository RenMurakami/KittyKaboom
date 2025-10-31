from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading

from game_client import GameClient
from game_server import GameServer
from game_system import NetworkLink


class OnlineSetup(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = None
        self.client = None

        # Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.info_label = Label(text="Setup online match", size_hint=(1, 0.2))
        layout.add_widget(self.info_label)

        self.room_input = TextInput(
            hint_text="Enter room name or server IP",
            size_hint=(1, 0.2)
        )
        self.room_input.text = "127.0.0.1"
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

    # -----------------------------
    # CLIENT SIDE
    # -----------------------------
    def join_room(self, instance):
        """Start client connection in a background thread."""
        self._update_label("Connecting to host...")
        threading.Thread(target=self._connect_to_host, daemon=True).start()

    def _connect_to_host(self):
        try:
            host_ip = self.room_input.text.strip()
            self.client = GameClient(host=host_ip, port=12345)
            network = NetworkLink(self.client.sock)

            print("[CLIENT] Connected to host, switching to game...")
            Clock.schedule_once(lambda dt: self._switch_to_game(network=network, is_host=False), 0)

        except Exception as e:
            err_msg = f"Failed to join: {e}"
            Clock.schedule_once(lambda dt, msg=err_msg: self._update_label(msg), 0)

    # -----------------------------
    # HOST SIDE
    # -----------------------------
    def host_room(self, instance):
        """Start server and wait for client connection in a background thread."""
        self._update_label("Starting server...")
        threading.Thread(target=self._start_server, daemon=True).start()

    def _start_server(self):
        try:
            self.server = GameServer(port=12345)
            self._update_label("Waiting for client to connect...")

            # Accept only one client before switching to game
            client_sock = self.server.accept_client()
            network = NetworkLink(client_sock)
            Clock.schedule_once(lambda dt: self._switch_to_game(network=network, is_host=True), 0)

        except Exception as e:
            err_msg = f"Failed to host: {e}"
            Clock.schedule_once(lambda dt, msg=err_msg: self._update_label(msg), 0)


    # -----------------------------
    # GAME SWITCH
    # -----------------------------
    def _switch_to_game(self, network=None, is_host=True):
        """Switch to the game screen with proper network setup."""
        if not network:
            print("[ERROR] Network object missing, cannot enter game.")
            return

        game_screen = self.manager.get_screen("stage1_1")
        game_screen.is_host = is_host
        game_screen.network = network

        # Kivy automatically calls on_enter; do not call manually
        self.manager.current = "stage1_1"

    # -----------------------------
    # UTILS
    # -----------------------------
    def _update_label(self, text):
        self.info_label.text = text

    def go_back(self, instance):
        self.manager.current = "match_select"
