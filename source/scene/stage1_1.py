# stage1_1.py
from stage_template import StageTemplate

class Stage1_1(StageTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wall_defs = [
            # === Outer boundaries ===
            (0.00, 0.00, 1.00, 0.02),   # ground (prevents tanks from rising)
            #(0.00, 0.98, 1.00, 0.02),   # ceiling
            (0.00, 0.00, 0.02, 1.00),   # left wall
            (0.98, 0.00, 0.02, 1.00),   # right wall

            # === Lower maze section ===
            (0.10, 0.15, 0.30, 0.01),   # lower left platform
            (0.40, 0.15, 0.01, 0.25),   # vertical wall up from lower left
            (0.10, 0.40, 0.31, 0.01),   # upper left floor

            (0.60, 0.15, 0.30, 0.01),   # lower right platform
            (0.60, 0.15, 0.01, 0.25),   # vertical wall up from lower right
            (0.60, 0.40, 0.31, 0.01),   # upper right floor

            # === Mid maze walls ===
            (0.25, 0.55, 0.01, 0.35),   # middle left vertical
            (0.25, 0.90, 0.30, 0.01),   # top mid floor
            (0.55, 0.55, 0.01, 0.35),   # middle right vertical
            (0.55, 0.70, 0.40, 0.01),   # mid horizontal floor

            # === Central corridor ===
            (0.40, 0.70, 0.20, 0.01),   # middle passage floor
            (0.40, 0.70, 0.01, 0.15),   # left wall of passage
            (0.59, 0.85, 0.01, 0.15),   # right wall of passage
        ]
