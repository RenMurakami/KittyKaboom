from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Scale, Rotate
import os

class FullTank(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size = (100, 100)

        # 画像パス
        base_path = os.path.join(os.path.dirname(__file__), "resource", "tankImage", "red")
        body_path = os.path.abspath(os.path.join(base_path, "body.png"))
        cannon_path = os.path.abspath(os.path.join(base_path, "cannon.png"))

        # --- Body ---
        self.body = Image(source=body_path, size_hint=(None, None), size=self.size, pos=self.pos)
        self.add_widget(self.body)

        # --- Cannon ---
        self.cannon = Image(source=cannon_path, size_hint=(None, None), size=self.size, pos=self.pos)
        self.add_widget(self.cannon)

        # --- 砲塔回転用 ---
        with self.cannon.canvas.before:
            self._cannon_push = PushMatrix()
            self._cannon_rotate = Rotate(angle=0, origin=self.center)
        with self.cannon.canvas.after:
            self._cannon_pop = PopMatrix()

        # --- 左右反転用 ---
        with self.canvas.before:
            self._push = PushMatrix()
            self._scale = Scale(1, 1, 1, origin=self.center)
        with self.canvas.after:
            self._pop = PopMatrix()

        self.facing_left = False
        self.cannon_angle = 0  # 砲塔の角度

        self.bind(pos=self._sync_images, size=self._sync_images)

    def _sync_images(self, *args):
        self.body.pos = self.pos
        self.body.size = self.size
        self.cannon.pos = self.pos
        self.cannon.size = self.size

        # --- 回転の基準点を調整 ---
        cx, cy = self.center
        # ここで微調整（例：少し上にずらす）
        cy -= self.height * 0.1  # ← 15% 上/下にずらす
        cx += self.width * 0.03  # ← 少し右にずらす

        self._scale.origin = (cx, cy)          # 左右反転の基準
        self._cannon_rotate.origin = (cx, cy)  # 砲塔回転の基準

    def flip_horizontal(self, left: bool):
        """左右反転"""
        if left == self.facing_left:
            return
        self.facing_left = left
        self._scale.x = -1 if left else 1

    def rotate_cannon(self, delta_angle: float):
        """砲塔の角度を回転（-80°〜+80°に制限）"""
        self.cannon_angle += delta_angle
        # --- 角度制限 ---
        if self.cannon_angle > 80:
            self.cannon_angle = 80
        elif self.cannon_angle < -80:
            self.cannon_angle = -80
        self._cannon_rotate.angle = self.cannon_angle
