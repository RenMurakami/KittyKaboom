from stage_template import StageTemplate
from ball import Ball

class Stage1_1(StageTemplate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wall_defs = [
            # === Outer boundaries ===
            (0.00, 0.00, 1.00, 0.02),
            (0.00, 0.00, 0.02, 1.00),
            (0.98, 0.00, 0.02, 1.00),

            # === Lower maze section ===
            (0.10, 0.15, 0.30, 0.01),
            (0.40, 0.15, 0.01, 0.25),
            (0.10, 0.40, 0.31, 0.01),

            (0.60, 0.15, 0.30, 0.01),
            (0.60, 0.15, 0.01, 0.25),
            (0.60, 0.40, 0.31, 0.01),

            # === Mid maze walls ===
            (0.25, 0.55, 0.01, 0.35),
            (0.25, 0.90, 0.30, 0.01),
            (0.55, 0.55, 0.01, 0.35),
            (0.55, 0.70, 0.40, 0.01),

            # === Central corridor ===
            (0.40, 0.70, 0.20, 0.01),
            (0.40, 0.70, 0.01, 0.15),
            (0.59, 0.85, 0.01, 0.15),
        ]
