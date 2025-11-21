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
    def __init__(self, **kw):
        super().__init__(**kw)
        self.network = None
        self.player_id = None
        self.is_host = None
    def on_enter(self, *args):
        # Create game widget
        p1_color = self.manager.p1_tank_color if hasattr(self.manager, 'p1_tank_color') else 'red'
        p2_color = self.manager.p2_tank_color if hasattr(self.manager, 'p2_tank_color') else 'blue'


        self.game = GameWidgetBase(
            p1_color,
            p2_color,
            network=self.network,
            player_id=self.player_id,
            is_host=self.is_host
        )

        self.add_widget(self.game)

        # Back button
        self.back_btn = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width - 110, self.height -100)
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
    SEND_HZ = 15 
    LOG_MAX_LINES = 10
    LOG_X = 10
    LOG_Y_START = 10
    LOG_LINE_HEIGHT = 20

    def __init__(self, p1_color='red', p2_color='blue', network=None, player_id=None, is_host=False,**kwargs):
        super().__init__(**kwargs)

        # --- Background ---
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # --- Tanks (2 players) ---
        # --- FullTank Instances (Set Colors Here) ---
        tank1 = FullTank(p1_color,pos=(self.width * 0.15, self.height))  
        tank2 = FullTank(p2_color,pos=(self.width * 0.85, self.height))  
        self.full_tanks = [tank1, tank2] 
        
        self.network = network
        self.player_id = player_id
        self.is_host = is_host
    

        for tank in self.full_tanks:
            self.add_widget(tank)
            
        self.tank_vy = [0 for _ in self.full_tanks]

        # Adjust tank position/size when window resizes
        self.bind(size=self._initialize_tank_positions)

        # physics / state
        self.tank_vy = [0 for _ in self.full_tanks]
        self.base_height = 720
        self.scale_y = 1.0
        self.vx = self.vy = 0
        self.gravity = -9.8 * 0.05
        self.friction = 0.98
        self.bounce = 0.7
        self.walls = []
        self.launch_speed = 20.0
        self.balls = []
        self.turn_timer = 10.0
        self.turn_state = "START_DROP"
        self.cannon_angle_speed = 1.0
        
        self.current_turn = 0
        self.active_tank = self.full_tanks[self.current_turn]
        self.is_current_turn = False

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
            
        # network receive callback binding: ensure UI thread scheduling
        if self.network:
            # assign a safe callback that schedules on main thread
            def _cb(msg):
                # schedule application of the message on main thread
                Clock.schedule_once(lambda dt: self.on_network_message(msg), 0)
            self.network.on_message = _cb

        # send throttling
        self._send_accum = 0.0

    
    # --- Tank Setup ---
    def _initialize_tank_positions(self, instance, value):
        """Adjust tank sizes when screen resizes."""
        tank_h = self.height * 0.10
        tank_w = tank_h * 1.5
        for i, tank in enumerate(self.full_tanks):
            tank.size = (tank_w, tank_h)
            tank.x = self.width * (0.15 if i == 0 else 0.85) - tank_w / 2
            if not hasattr(tank, "initialized"):
                tank.y = self.height + tank_h
                tank.initialized = True
            else:
                tank.y = tank.y / getattr(self, "old_height", self.height) * self.height
        self.old_height = self.height
        self.full_tanks[0].flip_horizontal(False)
        self.full_tanks[1].flip_horizontal(True)
        self._reposition_ui()

    # --- helpers for printing into UI
    def write(self, message):
        message = message.strip()
        if not message:
            return
        self.logs.append(message)
        # update label texts
        for i, lbl in enumerate(self.log_labels):
            idx = i - (self.LOG_MAX_LINES - len(self.logs))
            lbl.text = self.logs[idx] if idx >= 0 else ""
        sys.__stdout__.write(message + "\n")

    def flush(self):
        pass

    # --- layout updates
    def _update_bg(self, *args):
        self.bg_rect.pos = (0,0)
        self.bg_rect.size = (self.width, self.height)
        self.scale_y = self.height / self.base_height
        self.gravity = -9.8 * 0.05 * self.scale_y
        self.launch_speed = 20.0 * self.scale_y

    def _reposition_ui(self, *args):
        self.turn_label.pos = (10, self.height - self.turn_label.height - 10)

    # --- tank initialization / sizes
    def _initialize_tank_positions(self, instance, value):
        tank_h = self.height * 0.10
        tank_w = tank_h * 1.5
        for i, tank in enumerate(self.full_tanks):
            tank.size = (tank_w, tank_h)
            tank.x = self.width * (0.15 if i == 0 else 0.85) - tank_w/2
            if not hasattr(tank, "initialized"):
                tank.y = self.height + tank_h
                tank.initialized = True
            else:
                tank.y = tank.y / getattr(self, "old_height", self.height) * self.height
        self.old_height = self.height
        self.full_tanks[0].flip_horizontal(False)
        self.full_tanks[1].flip_horizontal(True)
        self._reposition_ui()

    # --- turn switching
    def _switch_turn(self, dt):
        # if host, announce turn switch so both clients keep turn in sync
        if self.network:
            self.network.send({"type": "turn_update", "current_turn": self.current_turn})

        print(f"🔄 Turn switched! Now controlling Tank {self.current_turn}")

    # --- launching ball
    def launch_ball(self):
        tank = self.active_tank
        angle_rad = math.radians(tank.cannon_angle)
        vx = self.launch_speed * math.cos(angle_rad)
        vy = self.launch_speed * math.sin(angle_rad)
        if tank.facing_left:
            vx *= -1

        offset_distance = tank.width * 0.6 * self.scale_y
        spawn_x = tank.center_x + math.cos(angle_rad) * offset_distance * (-1 if tank.facing_left else 1)
        spawn_y = tank.center_y + math.sin(angle_rad) * offset_distance

        new_ball = Ball(pos=(spawn_x, spawn_y))
        new_ball.velocity = Vector(vx, vy)
        new_ball.gravity_scale = self.gravity * self.scale_y
        new_ball.fired = True
        new_ball.owner = tank

        self.balls.append(new_ball)
        self.add_widget(new_ball)

        print(f"💥 FIRE! Angle: {tank.cannon_angle}° | Vx: {vx:.1f}, Vy: {vy:.1f}")

    # --- main update (called by BaseStage at 60Hz) ---
    def update_game_state(self, dt):
        """Main per-frame: physics, input, balls, network sync."""
        # Throttle outgoing sends
        self._send_accum += dt
        send_interval = 1.0 / self.SEND_HZ

        ax = ay = 0
        # my_tank: the tank this process is allowed to control directly
        my_tank = self.full_tanks[self.player_id]
        self.is_current_turn = my_tank is self.active_tank
        
        # --- START_DROP settling ---
        if self.turn_state == "START_DROP":
            all_settled = True
            for i, t in enumerate(self.full_tanks):
                self.tank_vy[i] += self.gravity
                new_y = t.y + self.tank_vy[i]

                collision_y = 1
                for wall in self.walls:
                    wx, wy = wall.pos
                    ww, wh = wall.size
                    if (t.x + t.width > wx and t.x < wx + ww) and (new_y <= wy + wh <= t.y):
                        collision_y = max(collision_y, wy + wh)

                if new_y <= collision_y:
                    new_y = collision_y
                    self.tank_vy[i] = 0
                else:
                    all_settled = False
                t.y = new_y

            if all_settled:
                self.turn_state = "INPUT"
                self.turn_timer = 10.0
                self.active_tank = self.full_tanks[self.current_turn]

        # --- Turn timer ---
        if self.turn_state == "INPUT":
            self.turn_timer -= dt * (self.scale_y)
            self.turn_label.text = f"Tank {self.current_turn + 1} Turn: {int(self.turn_timer)}s"

            if self.turn_timer <= 0:
                self.launch_ball()
                self.turn_state = "FIRING"
                self.vx = self.vy = 0

        # --- Input handling: only when it is this player's tank's turn AND this process owns that tank ---
        
        if self.turn_state == "INPUT" and self.is_current_turn:
            print("input handling")
            # accelerometer or keyboard
            if self.platform == "android":
                try:
                    accel = accelerometer.acceleration
                    if accel and all(a is not None for a in accel):
                        x, y, z = accel
                        ax = y * 0.3
                        if x > 1.5:
                            self.cannon_angle_speed=+self.cannon_angle_speed
                            self.active_tank.rotate_cannon(self.cannon_angle_speed)
                        elif x < -1.5:
                            self.cannon_angle_speed=-self.cannon_angle_speed
                            self.active_tank.rotate_cannon(self.cannon_angle_speed)
                except Exception:
                    pass
            else:
                if "left" in self._keys:  ax -= 1.0
                if "right" in self._keys: ax += 1.0
                if "up" in self._keys:    
                    #self.cannon_angle_speed=+self.cannon_angle_speed
                    self.active_tank.rotate_cannon(+self.cannon_angle_speed)
                if "down" in self._keys:  
                    #self.cannon_angle_speed=-self.cannon_angle_speed
                    self.active_tank.rotate_cannon(-self.cannon_angle_speed)

            # physics for controlled tank (horizontal movement)
            ay += self.gravity
            self.vx += ax
            self.vy += ay
            self.vx *= self.friction
            self.vy *= self.friction

            new_x = self.active_tank.x + self.vx
            new_y = self.active_tank.y + self.vy
            tank_w, tank_h = self.active_tank.size

            # boundaries & collisions with walls
            if new_x < 0:
                new_x, self.vx = 0, -self.vx * self.bounce
            elif new_x + tank_w > self.width:
                new_x, self.vx = self.width - tank_w, -self.vx * self.bounce
            if new_y < 0:
                new_y, self.vy = 0, -self.vy * self.bounce
            elif new_y + tank_h > self.height:
                new_y, self.vy = self.height - tank_h, -self.vy * self.bounce

            for wall in self.walls:
                if hasattr(wall, "blocks"):
                    for block in wall.blocks[:]:
                        if self.active_tank.collide_widget(block):
                            if abs((self.active_tank.center_x - block.center_x)) > abs((self.active_tank.center_y - block.center_y)):
                                self.vx *= -self.bounce
                                if self.active_tank.center_x < block.center_x:
                                    new_x = block.x - self.active_tank.width
                                else:
                                    new_x = block.right
                            else:
                                self.vy *= -self.bounce
                                if self.active_tank.center_y < block.center.center_y if False else True:
                                    # keep logic consistent with your original code:
                                    if self.active_tank.center_y < block.center_y:
                                        new_y = block.y - self.active_tank.height
                                    else:
                                        new_y = block.top

            # flip logic
            if self.vx > 0.1 and self.active_tank.facing_left:
                self.active_tank.flip_horizontal(False)
            elif self.vx < -0.1 and not self.active_tank.facing_left:
                self.active_tank.flip_horizontal(True)

            self.active_tank.pos = (new_x, new_y)
        else:
            print(f"self.is_current_turn={self.is_current_turn}")
            print(f"self.turn_state={self.turn_state}")
            
        # --- Ball updates (run locally for physics) ---
        #if tank is my_tank:
        balls_to_remove = []
        for ball in list(self.balls):
            ball.update(dt, self.walls, self.bounce)

            # collisions with tanks -> game over
            for t in self.full_tanks:
                if t.collide_widget(ball):
                    self.game_over(t, ball)
                    return

            # destroy destructible blocks
            for wall in self.walls:
                wall.destroy_at(ball.center, radius=ball.width / 2)

            if not ball.fired:
                balls_to_remove.append(ball)

        if balls_to_remove and self.turn_state == "FIRING":
            for b in balls_to_remove:
                if b in self.balls:
                    self.balls.remove(b)
                    try:
                        self.remove_widget(b)
                    except Exception:
                        pass
            if not self.balls and self.is_host:
                print("Enter to switch turn:")
                self._switch_turn(dt)
                
            

        # --- Network send (throttled) ---
        if self.network and self.network.authorized:
            if self._send_accum >= send_interval:
                self._send_accum = 0.0
                # Only send if this process controls the currently active tank (my_tank)
                # or always send your own state each frame (we send if my_tank exists)
                # Compose minimal game_state for the remote peer
                
                my_balls = [
                    {"x": b.x, 
                     "y": b.y, 
                     "vx": getattr(b, "velocity", Vector(0,0)).x if hasattr(b, "velocity") else getattr(b, "vx", 0),
                     "vy": getattr(b, "velocity", Vector(0,0)).y if hasattr(b, "velocity") else getattr(b, "vy", 0)}
                    for b in self.balls
                ]
                packet = {
                    "tank_id": self.player_id,
                    "x": my_tank.x,
                    "y": my_tank.y,
                    "angle": my_tank.cannon_angle,
                    "facing_left": my_tank.facing_left,
                    "balls": my_balls,
                    "turn_state": self.turn_state,
                    "turn_timer": self.turn_timer
                }
                # send using network (server will broadcast to other clients)
                self.network.send({"type": "game_state", **packet})

    # --- input handlers ---
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        self._keys.add(Window._system_keyboard.keycode_to_string(key))

    def _on_key_up(self, window, key, *args):
        self._keys.discard(Window._system_keyboard.keycode_to_string(key))

    # --- network message entrypoint on UI thread ---
    def on_network_message(self, msg):
        """
        Called on the main thread (NetworkClient sets this as a scheduled callback).
        msg is expected to be a dict with "type".
        """
        msg_type = msg.get("type")
        if msg_type == "game_state":
            self.apply_remote_state(msg)
        elif msg_type == "turn_update":
            self.apply_turn_state(msg)           
        elif msg_type in ("authorized", "ready"):
            # nothing to do here (screen switching handled in OnlineSelectScreen)
            pass

    def apply_turn_state(self,msg):
        self.current_turn = msg.get("turn_index")
        print(f"Game system received turn info {msg}")
        self.active_tank = self.full_tanks[self.current_turn]
        #self.is_current_turn = self.full_tanks[self.player_id] is self.active_tank
        self.turn_state = "INPUT"
        self.turn_timer = 10.0
        self.vx = self.vy = 0    
        print(f"Current state is {self.is_current_turn}")    

    def apply_remote_state(self, msg):
        """
        msg contains:
            - tank_id (0 or 1)
            - x,y,angle,facing_left
            - balls: list of {x,y,vx,vy}
            - turn_state, current_turn, turn_timer
        Apply these values to the other player's tank and recreate opponent balls.
        """
        try:
            remote_id = msg.get("tank_id")
            if remote_id is None:
                return
            if remote_id == self.player_id:
                # Ignore echoes of our own state
                return

            # update opponent tank
            opp_tank = self.full_tanks[remote_id]
            opp_tank.x = msg.get("x", opp_tank.x)
            opp_tank.y = msg.get("y", opp_tank.y)
            
            opp_tank.cannon_angle = msg.get("angle", opp_tank.cannon_angle)
            opp_tank.set_cannon()
            facing_left_update = msg.get("facing_left", opp_tank.facing_left)
            opp_tank.flip_horizontal(facing_left_update)
            

            # sync turn info
            self.turn_state = msg.get("turn_state", self.turn_state)
            self.turn_timer = msg.get("turn_timer", self.turn_timer)
        except Exception as e:
            print("❗ apply_remote_state error:", e)

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
            