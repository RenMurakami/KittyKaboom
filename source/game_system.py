from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import accelerometer
from full_tank import FullTank
from kivy.utils import platform as core_platform
from kivy.vector import Vector
from kivy.graphics import Color, Rectangle
from collections import deque
import math
import sys

from Ball import Ball

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
            
        # --- ADD THESE LINES HERE ---
        self.current_turn = 0 
        self.active_tank = self.full_tanks[self.current_turn]
        self.active_tank.flip_horizontal(False) 
        self.full_tanks[1].flip_horizontal(True) 
        
        # --- 物理系 ---
        self.vx, self.vy = 0, 0
        self.gravity =  -9.8 * 0.05
        self.friction = 0.98
        self.bounce = 0.7
        self.walls = []
        self.launch_speed = 20.0 # Initial projectile speed
        self.balls = [] # List for active projectiles
        self.turn_timer = 10.0 # <--- CRITICAL: Initialize the timer
        self.turn_state = 'INPUT' 
        # --- 砲塔回転速度 ---
        self.cannon_angle_speed = 1.0  # 1フレームあたりの角度変化

        # --- 10 秒ごとにターン切り替え ---
        #Clock.schedule_interval(self._switch_turn, 10)
        # --- UI for Turn Management ---
        # REMOVED: Clock.schedule_interval(self._switch_turn, 10)
        self.turn_label = Label(
            text=f"Tank {self.current_turn + 1} Turn: {int(self.turn_timer)}s",
            size_hint=(None, None), size=(300, 40), pos=(10, self.height - 60)
        )
        self.bind(size=self._reposition_ui)
        self.add_widget(self.turn_label)

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
        
        # --- UI for Turn Management (This is now safe to run) ---
        self.turn_label = Label(
            text=f"Tank {self.current_turn + 1} Turn: {int(self.turn_timer)}s",
            # ...
        )

        self.platform = core_platform
        self._keys = set()
        if self.platform != "android":
            Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

        # 現在タンクが左を向いているか
        self.current_facing_left = True  
            
    def _switch_turn(self, dt):
            """Switches control to the next tank, resets the state, and flips the tank."""
            
            # 1. Cycle to the next tank
            self.current_turn = (self.current_turn + 1) % len(self.full_tanks)
            self.active_tank = self.full_tanks[self.current_turn]
            
            # 2. CRITICAL FIX: Handle Flipping based on the new active tank index
            # Tank 1 (Index 0) faces right, Tank 2 (Index 1) faces left
            is_facing_left = self.current_turn == 1
            self.active_tank.flip_horizontal(is_facing_left)

            # 3. Reset physics and timer
            self.vx = 0
            self.vy = 0
            self.turn_timer = 10.0 
            
            # 4. CRITICAL FIX: Reset state to allow input for the new turn
            self.turn_state = 'INPUT' # <-- This is the key to resuming play!
            
            print(f"🔄 Turn switched! Now controlling Tank {self.current_turn+1}")

    
    def _reposition_ui(self, *args):
        """Keeps UI elements (like the timer label) anchored correctly."""
        self.turn_label.pos = (10, self.height - self.turn_label.height - 10)

    # --- 新規追加: ボール発射ロジック ---
    def launch_ball(self):
        """
        Calculates initial velocity and launches the ball from the active tank.
        """
        tank = self.active_tank
        angle_rad = math.radians(tank.cannon_angle)
        
        # Calculate initial velocity components (Vx and Vy)
        vx = self.launch_speed * math.cos(angle_rad)
        vy = self.launch_speed * math.sin(angle_rad)

        if tank.facing_left:
            # Reverse horizontal velocity if the tank is facing left
            vx *= -1
            
        # 1. Create the new Ball
        new_ball = Ball(pos=(tank.center_x, tank.center_y))
        new_ball.velocity = Vector(vx, vy)
        new_ball.gravity_scale = self.gravity 
        new_ball.fired = True
        
        # 2. Add to game state
        self.balls.append(new_ball)
        self.add_widget(new_ball)
        
        print(f"💥 FIRE! Angle: {tank.cannon_angle}° | V_x: {vx:.1f}, V_y: {vy:.1f}")
    
    
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
        
        # --- 1. Turn Timer Logic (Controls input phase) ---
        if self.turn_state == 'INPUT':
            self.turn_timer -= dt
            # Update turn_label text here

            if self.turn_timer <= 0:
                self.launch_ball()
                self.turn_state = 'FIRING' 
                self.vx = self.vy = 0 # Stop tank movement after firing
        
        # Check for platform to determine input source
        if self.turn_state == 'INPUT':
            if self.platform == "android":
                try:
                    # --- ACCELEROMETER/GYRO INPUT ---
                    accel = accelerometer.acceleration
                    
                    if accel and all(a is not None for a in accel):
                        x, y, z = accel
                        ax = y * 0.3

                        # --- CANNON ROTATION (Controlled via X-axis tilt) ---
                        # Use the X-axis (Roll/Forward-Backward Tilt) for cannon.
                        if x > 1.5:  # Tilt forward/backward (up)
                            tank.rotate_cannon(+self.cannon_angle_speed)
                        elif x < -1.5:  # Tilt forward/backward (down)
                            tank.rotate_cannon(-self.cannon_angle_speed)
                        
                
                except Exception:
                    # Handle plyer/accelerometer initialization errors
                    pass
                    
            # --- Desktop/Keyboard Control (Original logic retained) ---
            else:
                if 'left' in self._keys: ax -= 0.3
                if 'right' in self._keys: ax += 0.3
                if 'up' in self._keys:
                    tank.rotate_cannon(+self.cannon_angle_speed)
                if 'down' in self._keys:
                    tank.rotate_cannon(-self.cannon_angle_speed)

        # --- VERTICAL ACCELERATION (Gravity) ---
        ay += self.gravity

        # --- 速度更新 (Update Velocity) ---
        self.vx += ax
        self.vy += ay
        self.vx *= self.friction
        self.vy *= self.friction

        # --- 位置更新（今のターンのタンクだけ動かす）(Update Position) ---
        new_x = tank.x + self.vx
        new_y = tank.y + self.vy
        tank_w, tank_h = tank.size

        # --- 画面端補正 (Screen Edge Correction) ---
        if new_x < 0: new_x, self.vx = 0, -self.vx * self.bounce
        elif new_x + tank_w > self.width: new_x, self.vx = self.width - tank_w, -self.vx * self.bounce
        if new_y < 0: new_y, self.vy = 0, -self.vy * self.bounce
        elif new_y + tank_h > self.height: new_y, self.vy = self.height - tank_h, -self.vy * self.bounce

        # --- 壁との衝突 (Wall Collision) ---
        for wall in self.walls:
            wx, wy, ww, wh = wall.x, wall.y, wall.width, wall.height
            if (new_x < wx + ww and new_x + tank_w > wx and
                new_y < wy + wh and new_y + tank_h > wy):
                
                # 前フレーム位置 (Previous frame position)
                prev_x = tank.x
                prev_y = tank.y
                
                # 横からぶつかったか？ (Collision from side?)
                if prev_x + tank_w <= wx:  # 左から右へ衝突 (Collision left to right)
                    new_x = wx - tank_w
                    self.vx = -self.vx * self.bounce
                elif prev_x >= wx + ww:  # 右から左へ衝突 (Collision right to left)
                    new_x = wx + ww
                    self.vx = -self.vx * self.bounce
                
                # 縦からぶつかったか？ (Collision from top/bottom?)
                if prev_y + tank_h <= wy:  # 下から上へ衝突 (Collision bottom to top)
                    new_y = wy - tank_h
                    self.vy = -self.vy * self.bounce
                elif prev_y >= wy + wh:  # 上から下へ衝突 (Collision top to bottom)
                    new_y = wy + wh
                    self.vy = -self.vy * self.bounce
                    
        # --- 左右自動反転 (Automatic Horizontal Flip) ---
        if self.vx > 0.1 and tank.facing_left:
            tank.flip_horizontal(False)
        elif self.vx < -0.1 and not tank.facing_left:
            tank.flip_horizontal(True)

        tank.pos = (new_x, new_y)
        
        # --- 4. Projectile Update and Turn Switch ---
        balls_to_remove = []
        for ball in self.balls:
            ball.update(dt, self.walls, self.bounce)
            # The Ball class sets ball.fired = False when it stops moving/settles
            if not ball.fired:
                balls_to_remove.append(ball)

        # Cleanup and switch turn
        if balls_to_remove and self.turn_state == 'FIRING':
            for ball in balls_to_remove:
                self.balls.remove(ball)
                self.remove_widget(ball)

            if not self.balls: # Check if all projectiles are gone
                self._switch_turn(dt)
    
    # --- キー入力 ---
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        self._keys.add(Window._system_keyboard.keycode_to_string(key))

    def _on_key_up(self, window, key, *args):
        self._keys.discard(Window._system_keyboard.keycode_to_string(key))
