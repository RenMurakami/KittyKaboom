from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import accelerometer
from full_tank import FullTank
from kivy.utils import platform as core_platform
from kivy.graphics import Color, Rectangle
from collections import deque
import sys


class BaseStage(Screen):
    def on_enter(self, *args):
        self.game = GameWidgetBase()
        self.add_widget(self.game)

        # Backボタン
        self.back_btn = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width - 110, 10)
        )
        self.add_widget(self.back_btn)
        self.back_btn.bind(on_release=self.go_back)
        self.bind(size=self._reposition_button)

        if core_platform == "android":
            Clock.schedule_once(self._enable_accel, 2)

        Clock.schedule_interval(self.game.update_game_state, 1.0 / 60.0)

    def _reposition_button(self, *args):
        self.back_btn.pos = (self.width - self.back_btn.width - 10, 10)

    def go_back(self, *args):
        self.manager.current = "title"

    def _enable_accel(self, dt):
        try:
            accelerometer.enable()
            accel = accelerometer.acceleration
            if accel is None:
                print("⚠ accel is None")
            else:
                print(f"✅ accel enabled: {accel}")
        except Exception as e:
            print(f"⚠ accel enable failed: {e}")

    def on_leave(self, *args):
        if core_platform == "android":
            try:
                accelerometer.disable()
                print("✅ accelerometer disabled")
            except Exception as e:
                print(f"⚠ accelerometer disable failed: {e}")

        Clock.unschedule(self.game.update_game_state)
        self.remove_widget(self.game)


class GameWidgetBase(Widget):
    LOG_MAX_LINES = 50
    LOG_X = 10
    LOG_Y_START = 10
    LOG_LINE_HEIGHT = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --- 背景 ---
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # --- FullTank を 2 台 ---
        self.full_tanks = [
            FullTank(pos=(200, 400)),
            FullTank(pos=(600, 400))
        ]
        for tank in self.full_tanks:
            self.add_widget(tank)
        self.current_turn = 0  # どのタンクのターンか
        self.active_tank = self.full_tanks[self.current_turn]

        # --- 10 秒ごとにターン切り替え ---
        Clock.schedule_interval(self._switch_turn, 10)

        # --- ログ用 ---
        self.logs = deque(maxlen=self.LOG_MAX_LINES)
        self.log_labels = []
        for i in range(self.LOG_MAX_LINES):
            lbl = Label(
                text="",
                pos=(self.LOG_X, self.LOG_Y_START + i * self.LOG_LINE_HEIGHT),
                size_hint=(None, None),
                size=(400, 28),              # ← 高さを少し広めに
                font_size=20,                # ← フォントサイズ指定
                halign="left",
                valign="top",
                #text_size=(300, self.LOG_LINE_HEIGHT)
                text_size=(400, None)        # ← 折り返し無しで横幅固定
            )
            self.add_widget(lbl)
            self.log_labels.append(lbl)

        # --- print をログにも反映 ---
        sys.stdout = self
        sys.stderr = self

        # --- 物理系 ---
        self.vx, self.vy = 0, 0
        self.gravity = -0.5
        self.friction = 0.98
        self.bounce = 0.7
        self.walls = []

        # --- 砲塔回転速度 ---
        self.cannon_angle_speed = 1.0  # 1フレームあたりの角度変化


        self.platform = core_platform
        self._keys = set()
        if self.platform != "android":
            Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

        # 現在タンクが左を向いているか
        self.current_facing_left = True  

    def _switch_turn(self, dt):
        """10秒ごとに操作するタンクを切り替える"""
        self.current_turn = (self.current_turn + 1) % len(self.full_tanks)
        self.active_tank = self.full_tanks[self.current_turn]
        # 速度をリセット（前のタンクの速度を引き継がない）
        self.vx = 0
        self.vy = 0
        print(f"🔄 Turn switched! Now controlling Tank {self.current_turn+1}")


    # --- 背景更新 ---
    def _update_bg(self, *args):
        self.bg_rect.pos = (0, 0)
        self.bg_rect.size = (self.width, self.height)

    # --- print ログ処理 ---
    def write(self, message):
        message = message.strip()
        if not message:
            return

        # 1. ログを追加
        self.logs.append(message)

        # 2. 古いラベルを上に押し上げる
        for i, lbl in enumerate(self.log_labels):
            idx = i - (self.LOG_MAX_LINES - len(self.logs))
            if idx >= 0:
                lbl.text = self.logs[idx]
            else:
                lbl.text = ""

        # コンソールにも出力
        sys.__stdout__.write(message + "\n")

    def flush(self):
        pass

    # --- ゲームループ ---
    def update_game_state(self, dt):
        ax = ay = 0
        tank = self.active_tank
        if self.platform == "android":
            try:
                accel = accelerometer.acceleration
                if accel and all(a is not None for a in accel):
                    x, y, z = accel
                    ay = -y * 0.3  # ← 横だけ反映、縦方向は無視
                    ax += self.gravity  # ← 常に重力だけ適用
                    # --- ジャイロで砲塔角度変更 ---
                    if x > 1:
                        tank.rotate_cannon(+self.cannon_angle_speed)
                    elif x < -1:
                        tank.rotate_cannon(-self.cannon_angle_speed)
                else:
                    ax += self.gravity
            except Exception:
                ax += self.gravity
        else:
            if 'left' in self._keys: ax -= 0.3
            if 'right' in self._keys: ax += 0.3
            if 'up' in self._keys:
                tank.rotate_cannon(+self.cannon_angle_speed)
            if 'down' in self._keys:
                tank.rotate_cannon(-self.cannon_angle_speed)
            ay += self.gravity

        # --- 速度更新 ---
        self.vx += ax
        self.vy += ay
        self.vx *= self.friction
        self.vy *= self.friction

        # --- 位置更新（今のターンのタンクだけ動かす）---
        new_x = tank.x + self.vx
        new_y = tank.y + self.vy
        tank_w, tank_h = tank.size

        # --- 画面端補正 ---
        if new_x < 0: new_x, self.vx = 0, -self.vx * self.bounce
        elif new_x + tank_w > self.width: new_x, self.vx = self.width - tank_w, -self.vx * self.bounce
        if new_y < 0: new_y, self.vy = 0, -self.vy * self.bounce
        elif new_y + tank_h > self.height: new_y, self.vy = self.height - tank_h, -self.vy * self.bounce

        # --- 壁との衝突 ---
        for wall in self.walls:
            wx, wy, ww, wh = wall.x, wall.y, wall.width, wall.height
            if (new_x < wx + ww and new_x + tank_w > wx and
                new_y < wy + wh and new_y + tank_h > wy):
                
                # 前フレーム位置
                prev_x = tank.x
                prev_y = tank.y
        
                # 横からぶつかったか？
                if prev_x + tank_w <= wx:  # 左から右へ衝突
                    new_x = wx - tank_w
                    self.vx = -self.vx * self.bounce
                elif prev_x >= wx + ww:   # 右から左へ衝突
                    new_x = wx + ww
                    self.vx = -self.vx * self.bounce
        
                # 縦からぶつかったか？
                if prev_y + tank_h <= wy:  # 下から上へ衝突
                    new_y = wy - tank_h
                    self.vy = -self.vy * self.bounce
                elif prev_y >= wy + wh:   # 上から下へ衝突
                    new_y = wy + wh
                    self.vy = -self.vy * self.bounce
                
        # --- 左右自動反転 ---
        if self.vx > 0.1 and tank.facing_left:
            tank.flip_horizontal(False)
        elif self.vx < -0.1 and not tank.facing_left:
            tank.flip_horizontal(True)

        tank.pos = (new_x, new_y)

    # --- キー入力 ---
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        self._keys.add(Window._system_keyboard.keycode_to_string(key))

    def _on_key_up(self, window, key, *args):
        self._keys.discard(Window._system_keyboard.keycode_to_string(key))
