import os
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Scale, Rotate


class FullTank(Widget):
    """Tank widget with a body and a rotatable cannon, supporting horizontal flip."""

    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)

        # Paths
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

        # State
        self.facing_left = False
        self.cannon_angle = 0

        # Keep body and cannon synced with widget size/pos
        self.bind(pos=self._sync_images, size=self._sync_images)

    def _sync_images(self, *args):
        """Synchronize body/cannon size and position with the widget."""
        self.body.pos = self.pos
        self.body.size = self.size
        self.cannon.pos = self.pos
        self.cannon.size = self.size

        # Adjust rotation/flip origin slightly for better alignment
        cx, cy = self.center
        cy -= self.height * 0.1  # shift down
        cx += self.width * 0.03  # shift right

        self._scale.origin = (cx, cy)
        self._cannon_rotate.origin = (cx, cy)

    def flip_horizontal(self, left: bool):
        """Flip tank horizontally."""
        if left == self.facing_left:
            return
        self.facing_left = left
        self._scale.x = -1 if left else 1

    def rotate_cannon(self, delta_angle: float):
        """Rotate cannon within -80° to +80°."""
        self.cannon_angle = max(-80, min(80, self.cannon_angle + delta_angle))
        self._cannon_rotate.angle = self.cannon_angle
