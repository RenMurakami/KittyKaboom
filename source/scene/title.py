from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        btn1 = Button(text="Play Stage 1-1", size_hint=(1, 0.3))
        btn1.bind(on_release=lambda *a: self.change_scene("stage1_1"))

        btn2 = Button(text="Play Stage 1-2", size_hint=(1, 0.3))
        btn2.bind(on_release=lambda *a: self.change_scene("stage1_2"))

        layout.add_widget(btn1)
        layout.add_widget(btn2)

        self.add_widget(layout)

    def change_scene(self, scene_name):
        self.manager.current = scene_name
