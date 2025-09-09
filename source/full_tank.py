from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate
from kivy.uix.widget import Widget 
from kivy.uix.image import Image
import os

class FullTank(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        resource_path = os.path.join(os.path.dirname(__file__), "resource", "tankImage", "red", "full.jpg")
        self.image = Image(source=os.path.abspath(resource_path), size=self.size, pos=self.pos)
        self.add_widget(self.image)

        self.facing_left = True

        # --- 反転用に最初から Canvas に追加 ---
        with self.image.canvas.before:
            self._push = PushMatrix()
            self._scale = Scale(1, 1, 1, origin=self.center)
        with self.image.canvas.after:
            self._pop = PopMatrix()

        self.bind(pos=self._sync_image, size=self._sync_image)

    def _get_origin(self):
            # 左右反転の基準点は常に画像の中央
            return (self.center_x, self.center_y)

    def _sync_image(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size
        self._scale.origin = self._get_origin()

    def flip_horizontal(self, left: bool):
        if left == self.facing_left:
            return
        self.facing_left = left

        # 左右の基準点を更新（左向きのときは右端を基準に）
        if left:
            origin_x = self.x + self.width  # 右端を基準に反転
        else:
            origin_x = self.x              # 左端を基準に反転

        self._scale.origin = (origin_x, self.center_y)
        self._scale.x = -1 if left else 1
