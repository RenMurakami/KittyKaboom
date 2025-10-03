from game_system import BaseStage, GameWidgetBase
from Wall import Wall
from kivy.metrics import dp


class Stage1_2(BaseStage):
    def on_enter(self, *args):
        super().on_enter(*args)

        self.WALL_THICKNESS = dp(3)

        # --- Wall definitions (normalized x, y, w, h) ---
        # Using % of width/height so they scale with screen size
        self.wall_defs = [
            (0.20, 0.30, 0.30, 0.02),   # Bottom Horizontal Platform
            (0.495, 0.50, 0.01, 0.40),  # Center Vertical Barrier
            (0.50, 0.65, 0.30, 0.02),   # Top Horizontal Platform
        ]

        # Create walls
        self.game.walls = [Wall() for _ in self.wall_defs]
        for wall in self.game.walls:
            self.game.add_widget(wall)

        # Bind resize handler
        self.game.bind(size=self._reposition_walls)
        self._reposition_walls()

        # Give wall list to tanks
        for tank in self.game.full_tanks:
            tank.walls = self.game.walls

    def _reposition_walls(self, *args):
        """Recalculate wall positions/sizes based on window size."""
        gw, gh = self.game.width, self.game.height
        for wall, (nx, ny, nw, nh) in zip(self.game.walls, self.wall_defs):
            wall.pos = (gw * nx, gh * ny)
            wall.size = (
                gw * nw if nw > 0 else self.WALL_THICKNESS,
                gh * nh if nh > 0 else self.WALL_THICKNESS
            )
