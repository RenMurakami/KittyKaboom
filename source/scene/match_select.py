from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MatchSelect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        offline_btn = Button(text="Offline Match", size_hint=(0.5, 0.2), pos_hint={"center_x":0.5})
        online_btn = Button(text="Online Match", size_hint=(0.5, 0.2), pos_hint={"center_x":0.5})

        offline_btn.bind(on_release=self.start_offline_match)
        online_btn.bind(on_release=self.start_online_match)

        layout.add_widget(offline_btn)
        layout.add_widget(online_btn)

        self.add_widget(layout)

    def start_offline_match(self, instance):
        # Go to stage 1 or tank select for offline
        self.manager.current = "tank_select"
        print("Offline match selected")

    def start_online_match(self, instance):
        # Go to online setup screen (you'll need to create it)
        self.manager.current = "online_setup"
        print("Online match selected")
