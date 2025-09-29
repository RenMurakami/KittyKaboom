from game_system import BaseStage
from Wall import Wall

class Stage1_1(BaseStage):
    def on_enter(self, *args):
        super().on_enter(*args)

        # 壁を追加
        self.game.walls = [
            Wall(pos=(200, 150), size=(120, 20)),
            Wall(pos=(400, 350), size=(150, 20)),
            Wall(pos=(600, 250), size=(20, 180))
        ]
        for wall in self.game.walls:
            self.game.add_widget(wall)

        # FullTank 全員に壁リストを渡す
        for tank in self.game.full_tanks:
            tank.walls = self.game.walls
