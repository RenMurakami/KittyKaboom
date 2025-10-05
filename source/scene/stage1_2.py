# stage1_2.py
from stage_template import StageTemplate

class Stage1_2(StageTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wall_defs = [
            # Boundaries 
            (0.02, 0.02, 0.96, 0.01),   # bottom floor
            (0.02, 0.02, 0.01, 0.80),   # left wall
            (0.97, 0.02, 0.01, 0.80),   # right wall

            # Lower maze section
            (0.15, 0.20, 0.30, 0.01),
            (0.45, 0.20, 0.01, 0.25),
            (0.15, 0.45, 0.31, 0.01),

            (0.55, 0.20, 0.30, 0.01),
            (0.55, 0.20, 0.01, 0.25),
            (0.55, 0.45, 0.31, 0.01),

            # Upper maze section (narrower)
            (0.25, 0.60, 0.01, 0.20),
            (0.25, 0.80, 0.25, 0.01),
            (0.50, 0.60, 0.01, 0.20),
            (0.50, 0.60, 0.25, 0.01),
            (0.75, 0.60, 0.01, 0.20),

            # Central connector
            (0.35, 0.55, 0.30, 0.01),
        ]
