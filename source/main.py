from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.properties import StringProperty


# Import your scenes
from scene.title import TitleScreen
from scene.welcome import WelcomeScreen
from scene.stage1_1 import Stage1_1
from scene.stage1_2 import Stage1_2   # you’ll need to create this like stage1_1

from kivy.app import App
from scene.tank_select import TankSelectScreen 

class GameScreenManager(ScreenManager):
    
    p1_tank_color = StringProperty('red')  # Default for safety
    p2_tank_color = StringProperty('blue') # Default for safety
    
    def __init__(self, **kwargs):
        super().__init__(transition=FadeTransition(), **kwargs)

        # Add screens
        self.add_widget(WelcomeScreen(name="welcome"))
        self.add_widget(TitleScreen(name="title"))
        self.add_widget(Stage1_1(name="stage1_1"))
        self.add_widget(Stage1_2(name="stage1_2"))
        self.add_widget(TankSelectScreen(name="tank_select")) 

        # Start at title screen
        self.current = "welcome"

class BallRollerApp(App):
    def build(self):
        return GameScreenManager()

if __name__ == '__main__':
    # print("Game start !!")
    BallRollerApp().run()

