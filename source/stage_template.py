from kivy.metrics import dp
from kivy.clock import Clock
from Wall import Wall
from game_system import BaseStage
import threading
import time


class StageTemplate(BaseStage):
    WALL_THICKNESS = dp(3)

    def on_enter(self, *args):
        """Called when the scene is shown."""
        super().on_enter(*args)
        
        if not hasattr(self, "is_host"):
            print("[WARN] Stage started without host/client role set.")
            return

        if self.is_host:
            print("[HOST] Setting up game world.")
            self._setup_stage()
        else:
            print("[CLIENT] Waiting for host updates.")
            # client shouldn't spawn walls or tanks
            self._setup_client_stage()


        # --- Setup network sync ---
        if hasattr(self, "network"):
            # Save reference to original update
            self._original_update = self.update_game_state

            # Replace update loop only for the host
            if self.is_host:
                Clock.unschedule(self.update_game_state)
                Clock.schedule_interval(self._host_update, 1 / 60.0)

            # Start background listener for remote updates
            threading.Thread(
                target=self._listen_remote_updates, daemon=True
            ).start()
            
    def _setup_client_stage(self):
        self.game.walls = []
        self.game.full_tanks = []

            
    def _setup_stage(self):
        self.game.walls = [
            Wall(pos=(0, 0), size=(0, 0), block_size=dp(5))
            for _ in self.wall_defs
        ]
        for wall in self.game.walls:
            self.game.add_widget(wall)

        self.game.bind(size=self._reposition_walls)
        self._reposition_walls()

        for tank in self.game.full_tanks:
            tank.walls = self.game.walls

    # ----------------------------------------------------------------------
    #  Host runs game logic, sends positions to clients
    # ----------------------------------------------------------------------
    def _host_update(self, dt):
        """Host version of the update loop."""
        try:
            # Run normal physics and game logic
            self._original_update(dt)

            # Sync local (host) tank position to clients
            if hasattr(self, "local_tank") and hasattr(self, "network"):
                msg = f"POS {self.local_tank.x:.2f} {self.local_tank.y:.2f} {self.local_tank.cannon_angle:.2f}"
                self.network.send(msg)
        except Exception as e:
            print("[HOST] Update failed:", e)

    # ----------------------------------------------------------------------
    #  Handle wall scaling
    # ----------------------------------------------------------------------
    def _reposition_walls(self, *args):
        gw, gh = self.game.width, self.game.height
        for wall, (nx, ny, nw, nh) in zip(self.game.walls, self.wall_defs):
            wall.pos = (gw * nx, gh * ny)
            wall.size = (
                gw * nw if nw > 0 else self.WALL_THICKNESS,
                gh * nh if nh > 0 else self.WALL_THICKNESS,
            )
            wall.rebuild_blocks()

    # ----------------------------------------------------------------------
    #  Listen for messages from network (client or host)
    # ----------------------------------------------------------------------
    def _listen_remote_updates(self):
        """Both host and client listen for messages here."""
        while True:
            try:
                msg = self.network.recv()
                if not msg:
                    continue

                parts = msg.split()
                if not parts:
                    continue

                # --- Client receives tank positions from host ---
                if parts[0] == "POS" and len(parts) == 4 and not self.is_host:
                    _, x, y, rot = parts
                    self.remote_tank.x = float(x)
                    self.remote_tank.y = float(y)
                    self.remote_tank.cannon_angle = float(rot)

                # --- Host receives client inputs (movement, rotation) ---
                elif parts[0] == "INPUT" and self.is_host:
                    if len(parts) < 2:
                        continue
                    commands = parts[1]
                    Clock.schedule_once(
                        lambda dt: self._apply_remote_input(commands)
                    )

            except Exception as e:
                print("[NETWORK] Receive failed:", e)
                time.sleep(0.2)
                continue

    # ----------------------------------------------------------------------
    #  Apply movement commands from remote client
    # ----------------------------------------------------------------------
    def _apply_remote_input(self, commands):
        """Apply client key commands to remote tank (player 2)."""
        t = self.remote_tank
        move_speed = 5
        for cmd in commands:
            if cmd == "L":
                t.x -= move_speed
            elif cmd == "R":
                t.x += move_speed
            elif cmd == "U":
                t.rotate_cannon(+2)
            elif cmd == "D":
                t.rotate_cannon(-2)
