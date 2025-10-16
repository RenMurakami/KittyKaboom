from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
import math

class Wall(Widget):
    def __init__(self, pos=(0,0), size=(200,100), block_size=20, **kwargs):
        super().__init__(**kwargs)
        self.block_size = block_size
        self.blocks = []
        self.pos = pos
        self.size = size
        self.rebuild_blocks()

    def rebuild_blocks(self):
        # Prevent zero size
        if self.width == 0 or self.height == 0:
            return

        # Clear old blocks
        for block in self.blocks:
            self.remove_widget(block)
        self.blocks.clear()

        bx_count = max(1, int(self.width / self.block_size))
        by_count = max(1, int(self.height / self.block_size))

        # Center of the wall for gradient
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        max_dist = math.sqrt((self.width/2)**2 + (self.height/2)**2)
        if max_dist == 0:
            max_dist = 1  # safeguard

        for i in range(bx_count):
            for j in range(by_count):
                x = self.x + i * self.block_size
                y = self.y + j * self.block_size
                block = Widget(pos=(x, y), size=(self.block_size, self.block_size))

                # Distance from center
                bx_center = x + self.block_size / 2
                by_center = y + self.block_size / 2
                dist = math.sqrt((bx_center - cx)**2 + (by_center - cy)**2)
                edge_factor = min(1.0, dist / max_dist)  # 0=center, 1=edge

                # Radial gradient: center brown → edge green
                r = 0.4 * (1 - edge_factor) + 0.1 * edge_factor
                g = 0.25 * (1 - edge_factor) + 0.6 * edge_factor
                b = 0.1
                a = 1.0

                with block.canvas:
                    Color(r, g, b, a)
                    block.rect = Rectangle(pos=block.pos, size=block.size)

                block.bind(pos=self.update_block, size=self.update_block)
                self.add_widget(block)
                self.blocks.append(block)

    def update_block(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def destroy_at(self, point, radius=15):
        """Destroy blocks intersecting a circular area"""
        to_remove = []
        for block in self.blocks:
            bx, by = block.center
            dx = bx - point[0]
            dy = by - point[1]
            if dx*dx + dy*dy <= radius*radius:
                to_remove.append(block)

        for block in to_remove:
            self.remove_widget(block)
            self.blocks.remove(block)

    @staticmethod
    def wall_collides(widget, wall):
        """Return True if widget collides with any block of the wall."""
        return any(widget.collide_widget(block) for block in wall.blocks)
