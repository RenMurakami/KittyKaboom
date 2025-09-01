from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

# Import your scenes
from scene.title import TitleScreen
from scene.stage1_1 import Stage1_1
from scene.stage1_2 import Stage1_2   # you’ll need to create this like stage1_1


class GameScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(transition=FadeTransition(), **kwargs)

        # Add screens
        self.add_widget(TitleScreen(name="title"))
        self.add_widget(Stage1_1(name="stage1_1"))
        self.add_widget(Stage1_2(name="stage1_2"))

        # Start at title screen
        self.current = "title"


class BallRollerApp(App):
    def build(self):
        return GameScreenManager()


if __name__ == '__main__':
    BallRollerApp().run()
