from game_system import BaseStage, GameWidgetBase
from Wall import Wall


class Stage1_2(BaseStage):
    def on_enter(self, *args):
        super().on_enter(*args)

        # Walls unique to stage1_2
        self.game.walls = [
            Wall(pos=(200, 200), size=(300, 20)),
            Wall(pos=(400, 400), size=(20, 300)),
            Wall(pos=(600, 200), size=(300, 20))
        ]
        for wall in self.game.walls:
                    self.game.add_widget(wall)
        
        # FullTank 全員に壁リストを渡す
        for tank in self.game.full_tanks:
            tank.walls = self.game.walls
