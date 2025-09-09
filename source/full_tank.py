import os
from kivy.uix.widget import Widget
from kivy.uix.image import Image

class FullTank(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size = (100, 100)

        # APK でも動くように絶対パスを取得
        resource_path = os.path.join(os.path.dirname(__file__), "resource", "tankImage", "red", "full.jpg")
        resource_path = os.path.abspath(resource_path)

        self.image = Image(
            source=resource_path,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.image)

        self.bind(pos=self._sync_image)

    def _sync_image(self, *args):
        self.image.pos = self.pos
