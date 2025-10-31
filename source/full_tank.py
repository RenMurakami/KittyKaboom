import os
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Scale, Rotate

class FullTank(Widget):
    """Tank with body and rotatable cannon, supporting horizontal flip."""

    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        self.color_name = color

        base_path = os.path.join(os.path.dirname(__file__), "resource", "tankImage", color)
        body_path = os.path.join(base_path, "body.png")
        cannon_path = os.path.join(base_path, "cannon.png")

        # Tank body
        self.body = Image(source=body_path, fit_mode="contain")
        self.add_widget(self.body)

        # Tank cannon
        self.cannon = Image(source=cannon_path, fit_mode="contain")
        self.add_widget(self.cannon)

        # Cannon rotation
        with self.cannon.canvas.before:
            self._cannon_push = PushMatrix()
            self._cannon_rotate = Rotate(angle=0, origin=self.center)
        with self.cannon.canvas.after:
            self._cannon_pop = PopMatrix()

        # Horizontal flip (mirror)
        with self.canvas.before:
            self._push = PushMatrix()
            self._scale = Scale(1, 1, 1, origin=self.center)
        with self.canvas.after:
            self._pop = PopMatrix()

        self.facing_left = False
        self.cannon_angle = 0
        self.ready = False
        self.walls = []

        self.bind(pos=self._sync_images, size=self._sync_images)

    def _sync_images(self, *args):
        self.body.pos = self.pos
        self.body.size = self.size
        self.cannon.pos = self.pos
        self.cannon.size = self.size

        cx, cy = self.center
        cy -= self.height * 0.1
        cx += self.width * 0.03

        self._scale.origin = (cx, cy)
        self._cannon_rotate.origin = (cx, cy)

    def flip_horizontal(self, left: bool):
        if left == self.facing_left:
            return
        self.facing_left = left
        self._scale.x = -1 if left else 1

    def rotate_cannon(self, delta_angle: float):
        self.cannon_angle = max(-80, min(80, self.cannon_angle + delta_angle))
        self._cannon_rotate.angle = self.cannon_angle

    def collide_widget(self, other_widget):
        """Circular collision."""
        dx = self.center_x - other_widget.center_x
        dy = self.center_y - other_widget.center_y
        distance = (dx**2 + dy**2) ** 0.5
        radius_self = min(self.width, self.height) * 0.5
        radius_other = max(other_widget.width, other_widget.height) * 0.5
        return distance < (radius_self + radius_other)

    def update(self, dt):
        """Empty update for StageTemplate hook."""
        pass
