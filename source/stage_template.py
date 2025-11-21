from kivy.metrics import dp
from kivy.clock import Clock
from Wall import Wall
from game_system import BaseStage
import threading
import time


class StageTemplate(BaseStage):
    WALL_THICKNESS = dp(3)

    def on_enter(self, *args):
        """Called when the scene is shown."""
        super().on_enter(*args)
        
        self.game.walls = [
            Wall(pos=(0, 0), size=(0, 0), block_size=dp(5))
            for _ in self.wall_defs
        ]
        for wall in self.game.walls:
            self.game.add_widget(wall)

        self.game.bind(size=self._reposition_walls)
        self._reposition_walls()

        for tank in self.game.full_tanks:
            tank.walls = self.game.walls
        
    # ----------------------------------------------------------------------
    #  Handle wall scaling
    # ----------------------------------------------------------------------
    def _reposition_walls(self, *args):
        gw, gh = self.game.width, self.game.height
        for wall, (nx, ny, nw, nh) in zip(self.game.walls, self.wall_defs):
            wall.pos = (gw * nx, gh * ny)
            wall.size = (
                gw * nw if nw > 0 else self.WALL_THICKNESS,
                gh * nh if nh > 0 else self.WALL_THICKNESS,
            )
            wall.rebuild_blocks()


    def update(self, dt):
        super().update(dt)

        # 🔹 Only the host should broadcast
        if self.is_host:
            self.send_game_state()
