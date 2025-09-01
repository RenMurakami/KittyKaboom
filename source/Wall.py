from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color


class Wall(Widget):
    """
    A simple rectangular wall for the ball to collide with.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)  # Solid gray color
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        """Updates the wall's graphic to match its widget properties."""
        self.rect.pos = self.pos
        self.rect.size = self.size
