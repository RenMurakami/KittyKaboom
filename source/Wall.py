from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color

class Wall(Widget):
    def __init__(self, pos=(0,0), size=(100,20), block_size=10, **kwargs):
        super().__init__(**kwargs)
        self.block_size = block_size
        self.blocks = []
        self.rebuild_blocks()

    def rebuild_blocks(self):
        # Remove existing blocks
        for block in self.blocks:
            self.remove_widget(block)
        self.blocks.clear()

        bx_count = max(1, int(self.width / self.block_size))
        by_count = max(1, int(self.height / self.block_size))

        for i in range(bx_count):
            for j in range(by_count):
                x = self.x + i * self.block_size
                y = self.y + j * self.block_size
                block = Widget(pos=(x, y), size=(self.block_size, self.block_size))
                with block.canvas:
                    Color(0.5, 0.5, 0.5, 1)
                    block.rect = Rectangle(pos=block.pos, size=block.size)
                block.bind(pos=self.update_block, size=self.update_block)
                self.add_widget(block)
                self.blocks.append(block)

    def update_block(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def destroy_at(self, point, radius=15):
        """Destroy blocks that intersect a circular area"""
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

    def wall_collides(widget, wall):
        """Return True if widget collides with any block of the wall."""
        return any(widget.collide_widget(block) for block in wall.blocks)

