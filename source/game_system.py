from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import accelerometer
from kivy.utils import platform as core_platform
from kivy.vector import Vector
from kivy.graphics import Color, Rectangle
from collections import deque
import math
import sys

from full_tank import FullTank
from ball import Ball


class BaseStage(Screen):
    """
    Base game stage screen.
    Handles setup, game loop, and accelerometer control on Android.
    """
    def on_enter(self, *args):
        # Create game widget
        p1_color = self.manager.p1_tank_color if hasattr(self.manager, 'p1_tank_color') else 'red'
        p2_color = self.manager.p2_tank_color if hasattr(self.manager, 'p2_tank_color') else 'blue'

        
        self.game = GameWidgetBase(p1_color,p2_color)
        self.add_widget(self.game)

        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width - 110, 10)
        )
        self.add_widget(self.back_btn)
        self.back_btn.bind(on_release=self.go_back)
        self.bind(size=self._reposition_button)

        # Enable accelerometer on Android
        if core_platform == "android":
            Clock.schedule_once(self._enable_accel, 2)

        # Run game loop at 60 FPS
        Clock.schedule_interval(self.game.update_game_state, 1.0 / 60.0)

    def _reposition_button(self, *args):
        """Reposition back button when window resizes."""
        self.back_btn.pos = (self.width - self.back_btn.width - 10, 10)

    def go_back(self, *args):
        """Return to title screen."""
        self.manager.current = "title"

    def _enable_accel(self, dt):
        """Enable accelerometer on Android (if available)."""
        try:
            accelerometer.enable()
        except Exception as e:
            print(f"⚠ Failed to enable accelerometer: {e}")

    def on_leave(self, *args):
        """Cleanup when leaving stage."""
        if core_platform == "android":
            try:
                accelerometer.disable()
            except Exception as e:
                print(f"⚠ Failed to disable accelerometer: {e}")

        Clock.unschedule(self.game.update_game_state)
        self.remove_widget(self.game)


class GameWidgetBase(Widget):
    """
    Core game logic:
    - Tank control and turns
    - Ball launching
    - Physics simulation
    - Logging output
    """
    LOG_MAX_LINES = 10
    LOG_X = 10
    LOG_Y_START = 10
    LOG_LINE_HEIGHT = 20

    def __init__(self, p1_color='red', p2_color='blue',  **kwargs):
        super().__init__(**kwargs)

        # --- Background ---
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # --- Tanks (2 players) ---
        # --- FullTank Instances (Set Colors Here) ---
        tank1 = FullTank(p1_color,pos=(self.width * 0.15, self.height * 10))  
        tank2 = FullTank(p2_color,pos=(self.width * 0.85, self.height * 10))  
        
        self.full_tanks = [tank1, tank2] 

        for tank in self.full_tanks:
            self.add_widget(tank)
            
        self.tank_vy = [0 for _ in self.full_tanks]
        self.tank_target_y = [10, 10]

        # Adjust tank position/size when window resizes
        self.bind(size=self._initialize_tank_positions)

        self.current_turn = 0
        self.active_tank = self.full_tanks[self.current_turn]

        # --- Physics settings ---
        self.vx, self.vy = 0, 0
        self.gravity = -9.8 * 0.05
        self.friction = 0.98
        self.bounce = 0.7
        self.walls = []
        self.launch_speed = 20.0
        self.balls = []
        self.turn_timer = 10.0
        self.turn_state = "START_DROP"
        self.cannon_angle_speed = 1.0

        # --- Turn label ---
        self.turn_label = Label(
            text=f"Tank {self.current_turn + 1} Turn: {int(self.turn_timer)}s",
            size_hint=(None, None),
            size=(300, 40),
            pos=(10, self.height - 60)
        )
        self.bind(size=self._reposition_ui)
        self.add_widget(self.turn_label)

        # --- Logging system ---
        self.logs = deque(maxlen=self.LOG_MAX_LINES)
        self.log_labels = []
        for i in range(self.LOG_MAX_LINES):
            lbl = Label(
                text="",
                pos=(self.LOG_X, self.LOG_Y_START + i * self.LOG_LINE_HEIGHT),
                size_hint=(None, None),
                size=(400, 28),
                font_size=16,
                halign="left",
                valign="top",
                text_size=(400, None)
            )
            self.add_widget(lbl)
            self.log_labels.append(lbl)

        # Redirect print to in-game log
        sys.stdout = self
        sys.stderr = self

        # --- Platform detection ---
        self.platform = core_platform
        self._keys = set()
        if self.platform != "android":
            Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            

    # --- Tank Setup ---
    def _initialize_tank_positions(self, instance, value):
        """Adjust tank sizes when screen resizes.
        If the turn_state is START_DROP, position tanks above the top edge
        so they fall in. Otherwise place them on the ground.
        """
        tank_h = self.height * 0.10
        tank_w = tank_h * 1.5  # 1.5:1 aspect ratio

        for i, tank in enumerate(self.full_tanks):
            tank.size = (tank_w, tank_h)
            # X position (left / right)
            tank.x = self.width * (0.15 if i == 0 else 0.85) - tank_w / 2

            # Y: if we're about to drop, put the tanks above the screen top
            if getattr(self, "turn_state", None) == "START_DROP":
                # place them well above the top so they visibly fall
                tank.y = self.height + 150 + i * 40  # stagger slightly to avoid overlap
                # reset per-tank vertical velocity for fresh drop
                if len(self.tank_vy) > i:
                    self.tank_vy[i] = 0
                else:
                    # ensure list long enough
                    while len(self.tank_vy) <= i:
                        self.tank_vy.append(0)
            else:
                # normal ground placement
                base_y = 10
                tank.y = base_y

        # set facing
        self.full_tanks[0].flip_horizontal(False)
        self.full_tanks[1].flip_horizontal(True)

        self._reposition_ui()


    def _switch_turn(self, dt):
        """Switch control to the next tank."""
        self.current_turn = (self.current_turn + 1) % len(self.full_tanks)
        self.active_tank = self.full_tanks[self.current_turn]

        is_facing_left = self.current_turn == 1
        self.active_tank.flip_horizontal(is_facing_left)

        self.vx = self.vy = 0
        self.turn_timer = 10.0
        self.turn_state = "INPUT"

        print(f"🔄 Turn switched! Now controlling Tank {self.current_turn + 1}")

    def _reposition_ui(self, *args):
        """Reposition UI elements when window resizes."""
        self.turn_label.pos = (10, self.height - self.turn_label.height - 10)

    # --- Ball Launch ---
    def launch_ball(self):
        tank = self.active_tank
        angle_rad = math.radians(tank.cannon_angle)

        vx = self.launch_speed * math.cos(angle_rad)
        vy = self.launch_speed * math.sin(angle_rad)

        if tank.facing_left:
            vx *= -1

        # --- FIXED: spawn ball just outside the cannon
        offset_distance = tank.width * 0.6  # distance from tank center
        spawn_x = tank.center_x + math.cos(angle_rad) * offset_distance * (-1 if tank.facing_left else 1)
        spawn_y = tank.center_y + math.sin(angle_rad) * offset_distance

        new_ball = Ball(pos=(spawn_x, spawn_y))
        new_ball.velocity = Vector(vx, vy)
        new_ball.gravity_scale = self.gravity
        new_ball.fired = True
        new_ball.owner = tank  # so it doesn’t kill its own tank

        self.balls.append(new_ball)
        self.add_widget(new_ball)

        print(f"💥 FIRE! Angle: {tank.cannon_angle}° | Vx: {vx:.1f}, Vy: {vy:.1f}")


    # --- Background update ---
    def _update_bg(self, *args):
        self.bg_rect.pos = (0, 0)
        self.bg_rect.size = (self.width, self.height)

    # --- Logging ---
    def write(self, message):
        """Redirect print output to in-game log display."""
        message = message.strip()
        if not message:
            return

        self.logs.append(message)

        for i, lbl in enumerate(self.log_labels):
            idx = i - (self.LOG_MAX_LINES - len(self.logs))
            lbl.text = self.logs[idx] if idx >= 0 else ""

        sys.__stdout__.write(message + "\n")

    def flush(self):
        pass

    def move_with_collision(self, tank, dx, dy, blocks):
        steps = int(max(abs(dx), abs(dy)) // 1) + 1
        step_x = dx / steps
        step_y = dy / steps
        new_x, new_y = tank.x, tank.y

        # Horizontal
        for _ in range(steps):
            new_x += step_x
            tank.x = new_x
            for b in blocks:
                if tank.collide_widget(b):
                    # allow horizontal movement if tank is clearly above the block
                    if tank.y >= b.top - 2:
                        continue
                    new_x -= step_x
                    tank.x = new_x
                    self.vx *= -self.bounce
                    break

        # Vertical
        for _ in range(steps):
            new_y += step_y
            tank.y = new_y
            for b in blocks:
                if tank.collide_widget(b):
                    new_y -= step_y
                    tank.y = new_y
                    self.vy *= -self.bounce
                    break

        return new_x, new_y

    def game_over(self, tank, ball):
        """Handle game over when a tank is hit by a ball."""
        print(f"💀 Game Over! {tank.color_name} tank was hit!")

        # Stop the game loop
        Clock.unschedule(self.update_game_state)

        # Visual indicator (optional)
        with tank.canvas.after:
            Color(1, 0, 0, 0.5)
            tank.width = tank.width * 0.6
            tank.height = tank.height * 0.6
            Rectangle(pos=tank.pos, size=tank.size)

        # Optionally show a label
        self.add_widget(Label(
            text="GAME OVER",
            font_size=48,
            color=(1, 0, 0, 1),
            size_hint=(None, None),
            size=(400, 100),
            pos=(self.width/2 - 200, self.height/2 - 50)
        ))

    # --- Game Loop ---
    def update_game_state(self, dt):
        ax = ay = 0
        tank = self.active_tank
        
        if self.turn_state == "START_DROP":
            all_settled = True

            # build list of all block widgets from all walls (may be empty)
            all_blocks = [b for wall in self.walls for b in getattr(wall, "blocks", [])]

            for i, tank in enumerate(self.full_tanks):
                # simulate per-tank vertical velocity (vy positive up, gravity is negative)
                self.tank_vy[i] += self.gravity
                # small timestep scale so fall speed is not huge on first frame
                new_y = tank.y + self.tank_vy[i]

                # default floor collision
                collision_y = 1

                # check collision against blocks (not the wall container)
                for block in all_blocks:
                    bx, by = block.pos
                    bw, bh = block.size
                    # top of block
                    top_of_block = by + bh
                    # horizontal overlap between tank and block?
                    if (tank.x + tank.width > bx) and (tank.x < bx + bw):
                        # is the tank passing through the top of the block this frame?
                        if new_y <= top_of_block <= tank.y:
                            collision_y = max(collision_y, top_of_block)

                # land if collided with anything; otherwise still falling
                if new_y <= collision_y:
                    new_y = collision_y
                    self.tank_vy[i] = 0
                else:
                    all_settled = False

                tank.y = new_y

            # when all tanks have settled, switch to input state
            if all_settled:
                self.turn_state = "INPUT"
                self.vx = self.vy = 0
                self.turn_timer = 10.0
                self.active_tank = self.full_tanks[self.current_turn]


        # --- Turn timer ---
        if self.turn_state == "INPUT":
            self.turn_timer -= dt
            self.turn_label.text = f"Tank {self.current_turn + 1} Turn: {int(self.turn_timer)}s"

            if self.turn_timer <= 0:
                self.launch_ball()
                self.turn_state = "FIRING"
                self.vx = self.vy = 0

        # --- Input handling ---
        if self.turn_state == "INPUT":
            if self.platform == "android":
                try:
                    accel = accelerometer.acceleration
                    if accel and all(a is not None for a in accel):
                        x, y, z = accel
                        ax = y * 0.3
                        if x > 1.5:
                            tank.rotate_cannon(+self.cannon_angle_speed)
                        elif x < -1.5:
                            tank.rotate_cannon(-self.cannon_angle_speed)
                except Exception:
                    pass
            else:
                # Keyboard controls
                if "left" in self._keys:  ax -= 0.2
                if "right" in self._keys: ax += 0.2
                if "up" in self._keys:    tank.rotate_cannon(+self.cannon_angle_speed)
                if "down" in self._keys:  tank.rotate_cannon(-self.cannon_angle_speed)

                if "space" in self._keys:
                    self.launch_ball()
                    self.turn_state = "FIRING"
                    self.vx = self.vy = 0
                    self._keys.discard("space")

        # --- Physics ---
        ay += self.gravity
        self.vx += ax
        self.vy += ay
        self.vx *= self.friction
        self.vy *= self.friction

        new_x = tank.x + self.vx
        new_y = tank.y + self.vy
        tank_w, tank_h = tank.size

        # Screen boundaries
        if new_x < 0: new_x, self.vx = 0, -self.vx * self.bounce
        elif new_x + tank_w > self.width: new_x, self.vx = self.width - tank_w, -self.vx * self.bounce
        if new_y < 0: new_y, self.vy = 0, -self.vy * self.bounce
        elif new_y + tank_h > self.height: new_y, self.vy = self.height - tank_h, -self.vy * self.bounce

        # Tank vs wall block collisions
        all_blocks = [b for wall in self.walls for b in wall.blocks]
        new_x, new_y = self.move_with_collision(tank, self.vx, self.vy, all_blocks)
        tank.pos = (new_x, new_y)


        # Auto-flip tank based on velocity
        if self.vx > 0.1 and tank.facing_left:
            tank.flip_horizontal(False)
        elif self.vx < -0.1 and not tank.facing_left:
            tank.flip_horizontal(True)

        tank.pos = (new_x, new_y)

        # --- Ball updates ---
        balls_to_remove = []
        for ball in self.balls:
            # 1️⃣ Ball movement
            ball.update(dt, self.walls, self.bounce)

            # 2️⃣ Check tank collisions
            for tank in self.full_tanks:
                if tank.collide_widget(ball):
                    self.game_over(tank, ball)
                    return  # stop game immediately

            # 3️⃣ Destroy wall blocks
            for wall in self.walls:
                wall.destroy_at(ball.center, radius=ball.width/2)

            # 4️⃣ Ball settled
            if not ball.fired:
                balls_to_remove.append(ball)


        if balls_to_remove and self.turn_state == "FIRING":
            for ball in balls_to_remove:
                self.balls.remove(ball)
                self.remove_widget(ball)

            if not self.balls:
                self._switch_turn(dt)

    # --- Keyboard handlers ---
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        self._keys.add(Window._system_keyboard.keycode_to_string(key))

    def _on_key_up(self, window, key, *args):
        self._keys.discard(Window._system_keyboard.keycode_to_string(key))
