from kivy.metrics import sp
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
import os

BASE_DIR = os.path.dirname(__file__)

#Window.size = (800, 600)
class PawButton(ButtonBehavior, FloatLayout):
    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        # 肉球画像
        self.image = Image(
            source=image_source,
            size_hint=(0.5, 0.5),
            pos_hint={"x": 0.02, "y": 0.1},
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.image)

        # 中央に文字
        self.label = Label(
            text=text,
            color=(0, 0, 0, 1),
            font_size="30sp",
            bold=True,
            halign="center",
            valign="middle",
            pos_hint={"x": -0.23, "y": -0.2},
            size_hint=(1, 1)
        )
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

class RotatingLabel(Label):
    """回転できるラベル"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self.update_origin, size=self.update_origin)

    def update_origin(self, *args):
        self.rotation.origin = self.center

    def set_angle(self, angle):
        self.rotation.angle = angle

class ShadowLabel(RotatingLabel):
    """影付き回転ラベル"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shadow_color = (0, 0, 0, 0.6)  # デフォルト黒影
        self.shadow_offset = (3, -3)
        self.bind(pos=self._update_shadow, size=self._update_shadow, texture_size=self._update_shadow)

        with self.canvas.before:
            # 影を描画
            self._shadow_color_instruction = Color(*self.shadow_color)
            self._shadow_rect = Rectangle()

    def _update_shadow(self, *args):
        # ラベルの位置とサイズに合わせて影の位置も更新
        self._shadow_color_instruction.rgba = self.shadow_color
        self._shadow_rect.texture = self.texture
        self._shadow_rect.size = self.texture_size
        self._shadow_rect.pos = (
            self.x + self.shadow_offset[0],
            self.y + self.shadow_offset[1]
        )

    def set_shadow(self, color, offset=(3, -3)):
        self.shadow_color = color
        self.shadow_offset = offset
        self._update_shadow()

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # source/scene
        PROJECT_DIR = os.path.dirname(BASE_DIR)                # source/
        
        RESOURCE_DIR = os.path.join(PROJECT_DIR, "resource")
        
        background_path = os.path.join(RESOURCE_DIR, "background.jpg")
        paw_path = os.path.join(RESOURCE_DIR, "paw.png")

        # 背景画像
        self.bg = Image(
            source=background_path,
            size_hint=(1, 1),
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.bg.disabled = True  # 背景がタッチを邪魔しないようにする
        layout.add_widget(self.bg)

        self.title = ShadowLabel(
            text="Kitty Kaboon",
            font_size=sp(min(Window.width, Window.height) * 0.10), #self.get_scaled_font_size(),
            color=(1, 1, 1, 0),  # デフォルト白
            size_hint=(None, None),
        )
        self.title.texture_update()
        self.title.size = self.title.texture_size
        self.title.pos = (
            (Window.width - self.title.width) / 2,
            (Window.height * 0.7) - self.title.height / 2
        )
        self.title.color = (0.70, 0.34, 0.42, 1)  # 少し明るめの赤茶
        self.title.set_shadow((0.5, 0.2, 0.25, 1))  # 影は少し濃いめに
        
        layout.add_widget(self.title)


        

        # Start Button Setting
        self.start_button = PawButton(
            image_source=paw_path,
            text="Start Game",
        )
        
        self.start_button.bind(on_press=lambda *a: self.change_scene("stage1_1"))
        layout.add_widget(self.start_button)


        

        # 肉球スタンプ
        self.paw = Image(
                    source=paw_path,
                    size_hint=(0.2, 0.2),
                    #pos_hint={"x": -0.05, "y": -0.05},
                )

        self.paw.opacity = 0

        # 回転を追加
        with self.paw.canvas.before:
            PushMatrix()
            self.paw_rotate = Rotate(angle=0, origin=self.paw.center)
        with self.paw.canvas.after:
            PopMatrix()

        self.paw.bind(pos=self._update_paw_origin, size=self._update_paw_origin)
        layout.add_widget(self.paw)
        self.add_widget(layout)

        # Update paw position when title changes
        self.title.bind(pos=self.update_paw_position, size=self.update_paw_position, texture_size=self.update_paw_position)
        

        # タイトルのサイズが変わるたびに中央揃え & paw再配置
        #self.title.bind(texture_size=self.update_title_and_paw)
        #Window.bind(size=lambda *a: self.update_title_font())
        # Window サイズ変更時にタイトルと paw を再配置
        Window.bind(size=lambda *a: (
                                        self.update_title_font(), 
                                        self.update_title_and_paw())
                                     )
        

        # 効果音
        self.sound_boom = SoundLoader.load("source/resource/boom.wav")
        self.sound_paw = SoundLoader.load("source/resource/boom.wav")

        # アニメーション開始
        Clock.schedule_once(lambda dt: self.animate_title(), 0.5)
        # WelcomeScreen.__init__ の最後に追加
        Clock.schedule_once(lambda dt: self.update_paw_position(), 0.1)
        

    def change_scene(self, scene_name):
        self.manager.current = scene_name

    def update_title_and_paw(self, *args):
        """タイトルのサイズをtextureに合わせて中央揃えし、paw位置更新"""
        self.title.size = self.title.texture_size
        # 画面中央に配置
        self.title.x = (Window.width - self.title.width) / 2
        self.title.y = Window.height * 0.7 - self.title.height / 2
        self.update_paw_position()

    def get_scaled_font_size(self):
        # 幅と高さの小さい方に基づいてフォントサイズを決める
        base = min(Window.width, Window.height)
        return sp(base * 0.12)  # 画面サイズの約12%

    def update_title_font(self):
        self.title.font_size = self.get_scaled_font_size()

    def animate_title(self):
        self.title.set_angle(0)
        anim = Animation(#color=(1, 1, 1, 1),
                         #font_size=self.get_scaled_font_size(),
                         duration=1.5)
        anim.bind(on_progress=self.rotate_title,
                  on_complete=lambda *a: self.animate_paw())
        anim.start(self.title)

        # 音
        if self.sound_boom:
            self.sound_boom.play()

    def rotate_title(self, anim, widget, progress):
        # progress: 0〜1
        self.title.set_angle(progress * 720)  # 2回転

    def _update_paw_origin(self, *args):
        self.paw_rotate.origin = self.paw.center

    def update_paw_position(self, *args):
        """'n' の右上に paw を配置 & Window サイズに応じてサイズ調整"""
        if not self.title.texture_size:
            return

        title_x, title_y = self.title.pos
        title_w, title_h = self.title.texture_size

        # 1) サイズスケーリング
        #base = Window.height  # ← 縦を基準にする
        #paw_size = base * 0.15  # 画面の 15% に設定
        #paw_size = max(120, min(paw_size, 220))  # 下限120px、上限220px
        #self.paw.size = (paw_size, paw_size)

        # 2) 位置更新
        n_right_x = title_x + title_w
        n_top_y = title_y + title_h

        offset_y = self.paw.height * 0.03
        offset_x = self.paw.width * 0.1
        self.paw.pos = (
            n_right_x,# - self.paw.width * 0.5,
            n_top_y# - self.paw.height * 0.5
        )

    def set_paw_angle(self, angle):
        """外部から角度を変更する用"""
        self.paw_rotate.angle = angle

    def animate_paw(self):
        # 肉球がポンッと出る
        self.paw.opacity = 1
        self.paw.size = (10, 10)
        self.paw_rotate.angle = -30  # ← 中心基準で30度回転
        anim = Animation(size=(120, 120), duration=0.3, t="out_bounce") + \
               Animation(size=(80, 80), duration=0.2)
        anim.start(self.paw)

        # 音
        if self.sound_paw:
            self.sound_paw.play()
            
