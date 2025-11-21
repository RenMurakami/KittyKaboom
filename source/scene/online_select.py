from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from network.client import NetworkClient
from kivy.clock import Clock

class OnlineSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network = None

        layout = BoxLayout(orientation='vertical', spacing=10, padding=50)

        self.keyword_input = TextInput(hint_text="Enter room keyword", size_hint=(1, 0.2))
        self.make_btn = Button(text="Create Room (Host)", size_hint=(1, 0.3))
        self.join_btn = Button(text="Join Room (Client)", size_hint=(1, 0.3))
        self.status_label = Button(text="Status: Not connected", size_hint=(1, 0.2))

        self.make_btn.bind(on_press=self.make_room)
        self.join_btn.bind(on_press=self.join_room)

        layout.add_widget(self.keyword_input)
        layout.add_widget(self.make_btn)
        layout.add_widget(self.join_btn)
        layout.add_widget(self.status_label)
        self.add_widget(layout)

    def make_room(self, instance):
        self.start_network(is_host=True)

    def join_room(self, instance):
        self.start_network(is_host=False)

    def start_network(self, is_host=False):
        keyword = self.keyword_input.text.strip()
        if not keyword:
            self.status_label.text = "Enter a keyword first!"
            return

        if not self.network:
            self.network = NetworkClient(keyword=keyword, is_host = is_host, on_message=self.on_message)
            self.network.start()
            self.status_label.text = "Connected. Waiting for other player…"

    def on_message(self, msg):
        # Use Clock to update UI from background thread
        Clock.schedule_once(lambda dt: self.handle_message(msg))

    def handle_message(self, msg):
        if msg["type"] == "authorized":
            self.status_label.text = "Keyword matched! Starting game…"
            self.network.send({"type": "ready"})
            Clock.schedule_once(lambda dt: self.start_game(), 0)
        elif msg["type"] == "ready":
            self.status_label.text = "Keyword matched! Starting game…"
            Clock.schedule_once(lambda dt: self.start_game(), 0)
        elif msg["type"] == "unauthorized":
            self.status_label.text = "Keyword mismatch!"


    def start_game(self):
        game_screen = self.manager.get_screen("stage1_1")
        game_screen.network = self.network

        # host = player 0, client = player 1
        if self.network.is_host:
            game_screen.player_id = 0
            game_screen.is_host = True
        else:
            game_screen.player_id = 1
            game_screen.is_host = False

        self.manager.current = "stage1_1"
