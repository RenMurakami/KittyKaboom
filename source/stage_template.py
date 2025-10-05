# stage_template.py
from kivy.metrics import dp
from Wall import Wall
from game_system import BaseStage

class StageTemplate(BaseStage):
    WALL_THICKNESS = dp(3)

    def on_enter(self, *args):
        super().on_enter(*args)

        # Create Wall widgets from definitions
        self.game.walls = [
            Wall(pos=(0, 0), size=(0, 0), block_size=dp(5))
            for _ in self.wall_defs
        ]
        for wall in self.game.walls:
            self.game.add_widget(wall)

        # Bind resize handler
        self.game.bind(size=self._reposition_walls)
        self._reposition_walls()

        # Pass wall list to tanks
        for tank in self.game.full_tanks:
            tank.walls = self.game.walls

    def _reposition_walls(self, *args):
        gw, gh = self.game.width, self.game.height
        for wall, (nx, ny, nw, nh) in zip(self.game.walls, self.wall_defs):
            wall.pos = (gw * nx, gh * ny)
            wall.size = (
                gw * nw if nw > 0 else self.WALL_THICKNESS,
                gh * nh if nh > 0 else self.WALL_THICKNESS,
            )
            wall.rebuild_blocks()
