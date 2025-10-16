import os
from kivy.metrics import sp
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen


BASE_DIR = os.path.dirname(__file__)


class PawButton(ButtonBehavior, FloatLayout):
    """Custom button with a paw image and centered label."""

    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)

        # Paw image
        self.image = Image(
            source=image_source,
            size_hint=(0.5, 0.5),
            pos_hint={"x": 0.02, "y": 0.1},
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.image)

        # Button label (centered text over paw)
        self.label = Label(
            text=text,
            color=(0, 0, 0, 1),
            font_size="30sp",
            bold=True,
            halign="center",
            valign="middle",
            pos_hint={"x": -0.23, "y": -0.2},
            size_hint=(1, 1),
        )
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)


class RotatingLabel(Label):
    """Label that supports rotation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()

        self.bind(pos=self.update_origin, size=self.update_origin)

    def update_origin(self, *args):
        self.rotation.origin = self.center

    def set_angle(self, angle):
        self.rotation.angle = angle


class ShadowLabel(RotatingLabel):
    """Rotating label with a drop shadow."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shadow_color = (0, 0, 0, 0.6)
        self.shadow_offset = (3, -3)

        with self.canvas.before:
            self._shadow_color_instruction = Color(*self.shadow_color)
            self._shadow_rect = Rectangle()

        self.bind(
            pos=self._update_shadow,
            size=self._update_shadow,
            texture_size=self._update_shadow,
        )

    def _update_shadow(self, *args):
        self._shadow_color_instruction.rgba = self.shadow_color
        self._shadow_rect.texture = self.texture
        self._shadow_rect.size = self.texture_size
        self._shadow_rect.pos = (
            self.x + self.shadow_offset[0],
            self.y + self.shadow_offset[1],
        )

    def set_shadow(self, color, offset=(3, -3)):
        self.shadow_color = color
        self.shadow_offset = offset
        self._update_shadow()


class WelcomeScreen(Screen):
    """Welcome screen with animated title and paw stamp."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Paths
        project_dir = os.path.dirname(BASE_DIR)
        resource_dir = os.path.join(project_dir, "resource")
        background_path = os.path.join(resource_dir, "background.jpg")
        paw_path = os.path.join(resource_dir, "paw.png")

        # Background image
        self.bg = Image(
            source=background_path,
            size_hint=(1, 1),
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False,
        )
        self.bg.disabled = True  # Background doesn’t intercept touches
        layout.add_widget(self.bg)

        # Title label
        self.title = ShadowLabel(
            text="Kitty Kaboon",
            font_size=sp(min(Window.width, Window.height) * 0.10),
            color=(0.70, 0.34, 0.42, 1),
            size_hint=(None, None),
        )
        self.title.texture_update()
        self.title.size = self.title.texture_size
        self.title.pos = (
            (Window.width - self.title.width) / 2,
            (Window.height * 0.7) - self.title.height / 2,
        )
        self.title.set_shadow((0.5, 0.2, 0.25, 1))
        layout.add_widget(self.title)

        # Start button
        self.start_button = PawButton(
            image_source=paw_path,
            text="Start Game",
        )
        self.start_button.bind(on_press=lambda *a: self.change_scene("match_select" ))
        layout.add_widget(self.start_button)

        # Paw stamp (animated)
        self.paw = Image(
            source=paw_path,
            size_hint=(0.2, 0.2),
            opacity=0,
        )
        with self.paw.canvas.before:
            PushMatrix()
            self.paw_rotate = Rotate(angle=0, origin=self.paw.center)
        with self.paw.canvas.after:
            PopMatrix()
        self.paw.bind(pos=self._update_paw_origin, size=self._update_paw_origin)
        layout.add_widget(self.paw)

        self.add_widget(layout)

        # Sync title and paw
        self.title.bind(
            pos=self.update_paw_position,
            size=self.update_paw_position,
            texture_size=self.update_paw_position,
        )
        Window.bind(size=lambda *a: (self.update_title_font(), self.update_title_and_paw()))

        # Sounds
        self.sound_boom = SoundLoader.load(os.path.join(resource_dir, "boom.wav"))
        self.sound_paw = SoundLoader.load(os.path.join(resource_dir, "boom.wav"))

        # Initial animations
        Clock.schedule_once(lambda dt: self.animate_title(), 0.5)
        Clock.schedule_once(lambda dt: self.update_paw_position(), 0.1)

    # --- Scene & UI updates ---

    def change_scene(self, scene_name):
        self.manager.current = scene_name

    def update_title_and_paw(self, *args):
        """Resize and reposition title; update paw accordingly."""
        self.title.size = self.title.texture_size
        self.title.x = (Window.width - self.title.width) / 2
        self.title.y = Window.height * 0.7 - self.title.height / 2
        self.update_paw_position()

    def get_scaled_font_size(self):
        return sp(min(Window.width, Window.height) * 0.12)

    def update_title_font(self):
        self.title.font_size = self.get_scaled_font_size()

    # --- Animations ---

    def animate_title(self):
        self.title.set_angle(0)
        anim = Animation(duration=1.5)
        anim.bind(on_progress=self.rotate_title, on_complete=lambda *a: self.animate_paw())
        anim.start(self.title)

        if self.sound_boom:
            self.sound_boom.play()

    def rotate_title(self, anim, widget, progress):
        self.title.set_angle(progress * 720)  # 2 rotations

    def _update_paw_origin(self, *args):
        self.paw_rotate.origin = self.paw.center

    def update_paw_position(self, *args):
        """Position paw near the top-right of the title."""
        if not self.title.texture_size:
            return

        title_x, title_y = self.title.pos
        title_w, title_h = self.title.texture_size
        self.paw.pos = (title_x + title_w, title_y + title_h)

    def set_paw_angle(self, angle):
        self.paw_rotate.angle = angle

    def animate_paw(self):
        self.paw.opacity = 1
        self.paw.size = (10, 10)
        self.paw_rotate.angle = -30

        anim = (
            Animation(size=(120, 120), duration=0.3, t="out_bounce")
            + Animation(size=(80, 80), duration=0.2)
        )
        anim.start(self.paw)

        if self.sound_paw:
            self.sound_paw.play()
