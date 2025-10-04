from kivy.metrics import dp
from Wall import Wall
from game_system import BaseStage, GameWidgetBase

class Stage1_1(BaseStage):
    """
    Stage 1-1 with walls that resize when window resizes.
    """

    def on_enter(self, *args):
        super().on_enter(*args)

        self.WALL_THICKNESS = dp(3)

        # Normalized wall definitions (x, y, w, h) all in 0–1 space
        self.wall_defs = [
            # (x, y, width, height)
            (0.05, 0.30, 0.20, 0.01),  
            (0.35, 0.55, 0.15, 0.01), 
            (0.50, 0.55, 0.15, 0.01), 
            (0.75, 0.80, 0.20, 0.01), 
            (0.30, 0.55, 0.005, 0.40),
            (0.95, 0.55, 0.005, 0.40), 
        ]

        # Create Wall widgets
        self.game.walls = [
            Wall(
                pos=(0, 0),       # placeholder, will be set by _reposition_walls
                size=(0, 0),      # placeholder, will be set by _reposition_walls
                block_size=dp(5)  # optional, size of each mini-block
            )
            for _ in self.wall_defs
        ]

        for wall in self.game.walls:
            self.game.add_widget(wall)

        # Bind resize handler
        self.game.bind(size=self._reposition_walls)
        self._reposition_walls()

        # Give wall list to tanks
        for tank in self.game.full_tanks:
            tank.walls = self.game.walls

    def _reposition_walls(self, *args):
        gw, gh = self.game.width, self.game.height
        for wall, (nx, ny, nw, nh) in zip(self.game.walls, self.wall_defs):
            wall.pos = (gw * nx, gh * ny)
            wall.size = (gw * nw if nw > 0 else self.WALL_THICKNESS,
                        gh * nh if nh > 0 else self.WALL_THICKNESS)
            # Recreate blocks if size changed
            wall.rebuild_blocks()

    def rebuild_blocks(self):
        # Remove old blocks
        for b in self.blocks:
            self.remove_widget(b)
        self.blocks.clear()

        # Recreate blocks based on new size
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


