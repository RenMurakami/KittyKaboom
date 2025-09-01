from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform as core_platform
from plyer import accelerometer
from Ball import Ball


class BaseStage(Screen):
    """
    Base class for all stages. It manages GameWidgetBase and back-to-title button.
    """
    def on_enter(self, *args):
        self.game = GameWidgetBase()
        self.add_widget(self.game)

        # Back-to-title button
        self.back_btn = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width - 110, 10)
        )
        self.add_widget(self.back_btn)
        self.back_btn.bind(on_release=self.go_back)
        self.bind(size=self._reposition_button)

        Clock.schedule_interval(self.game.update_game_state, 1.0 / 60.0)

    def on_leave(self, *args):
        Clock.unschedule(self.game.update_game_state)
        self.remove_widget(self.game)
        self.remove_widget(self.back_btn)

    def _reposition_button(self, *args):
        """Keep button at bottom-right when screen resizes."""
        self.back_btn.pos = (self.width - self.back_btn.width - 10, 10)

    def go_back(self, *args):
        """Return to the title screen."""
        self.manager.current = "title"


class GameWidgetBase(Widget):
    """
    Common game logic: ball, input, debug text.
    Stages will subclass this and add their own walls/layout.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create ball
        self.ball = Ball(size=(50, 50))
        self.add_widget(self.ball)
        self.bind(size=self.center_ball)

        # Debug label always top-left
        self.debug_label = Label(
            text="Debug",
            size_hint=(None, None),
            pos=(10, self.height - 30)
        )
        self.add_widget(self.debug_label)
        self.bind(size=self._reposition_debug)

        # Platform-specific input
        self.platform = core_platform
        if self.platform == "android":
            try:
                accelerometer.enable()
            except NotImplementedError:
                print("Accelerometer not implemented on this platform")
        else:
            self.on_key_down = self._on_key_down
            self.on_key_up = self._on_key_up
            self._keys = set()
            Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        # Walls will be set by child stages
        self.walls = []

    def _reposition_debug(self, *args):
        """Keep debug label at top-left corner."""
        self.debug_label.pos = (10, self.height - 30)

    def center_ball(self, *args):
        self.ball.center = self.center

    def update_game_state(self, dt):
        bounce_factor = 0.6

        if self.platform == "android":
            accel = accelerometer.acceleration
            if accel and all(a is not None for a in accel):
                x, y, z = accel
                input_vec = Vector(-x, -y)
                if input_vec.length() < 0.05:
                    input_vec = Vector(0, 0)
                self.ball.velocity += input_vec * 0.2
                self.ball.velocity *= 0.95
                self.debug_label.text = f"x={x:.2f}, y={y:.2f}, v=({self.ball.velocity.x:.2f},{self.ball.velocity.y:.2f})"
        else:
            vx = vy = 0
            if 'left' in self._keys: vx -= 1
            if 'right' in self._keys: vx += 1
            if 'up' in self._keys: vy += 1
            if 'down' in self._keys: vy -= 1
            self.ball.velocity += Vector(vx, vy) * 0.5
            self.ball.velocity *= 0.95
            self.debug_label.text = f"pos=({self.ball.x:.0f}, {self.ball.y:.0f}), v=({self.ball.velocity.x:.2f},{self.ball.velocity.y:.2f})"

        self.ball.update(dt, self.walls)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        self._keys.add(Window._system_keyboard.keycode_to_string(key))

    def _on_key_up(self, window, key, *args):
        self._keys.discard(Window._system_keyboard.keycode_to_string(key))
