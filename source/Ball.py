import math
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.graphics import Ellipse, Color, InstructionGroup
from kivy.uix.label import Label
import time

class Ball(Widget):
    """The projectile ball, updated for physics, gravity, and firing state."""
    velocity = Vector(0, 0)
    gravity_scale = 0.0  
    fired = False  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bounce_count = 0  # Initialize bounce counter
        self.size = (20, 20)
        self.center_x = self.x 
        self.center_y = self.y
        
        self.fired = False 
        self.velocity = Vector(0, 0)
        self.gravity_scale = 0.0 # Will be set by GameWidgetBase
        self.friction = 0.99
        self.bounce_limit = 2
        self.bounce_count = 0

        # Draw the base ball
        with self.canvas:
            self.outer_color = Color(1, 1, 1, 0)
            self.outer_ellipse = Ellipse(pos=self.pos, size=self.size)

        # InstructionGroup for the gradient to allow easy clearing and redrawing
        self.gradient_group = InstructionGroup()
        self.canvas.add(self.gradient_group)

        self.time_offset = time.time()
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        """Updates the position and size of the outer ellipse."""
        self.outer_ellipse.pos = self.pos
        self.outer_ellipse.size = self.size

    def update(self, dt, walls, bounce_factor):
        """Moves the ball and calculates new physics state."""
        if not self.fired:
            # If the ball is not fired, it should not update.
            return
            
        # 1. Apply Gravity
        self.velocity.y += self.gravity_scale

        # 2. Apply Position Update
        new_pos = self.pos[0] + self.velocity.x, self.pos[1] + self.velocity.y
        old_x, old_y = self.x, self.y       

        # 3. Apply Friction (Air Resistance)
        self.velocity.x *= self.friction
        self.velocity.y *= self.friction

        # 4. Check Window Bounds (Floor and Screen Edges)
        if new_pos[1] < 0: # Floor collision
            new_pos = new_pos[0], 0
            self.velocity.y = -self.velocity.y * bounce_factor
            self.velocity.x *= 0.8 # Additional ground friction
            self.bounce_count += 1
            
            # CRITICAL TERMINATION 1: Ball settles on the ground
            if abs(self.velocity.y) < 1 and abs(self.velocity.x) < 1:
                self.velocity = Vector(0, 0)
                self.fired = False # <--- MUST BE SET TO FALSE
                return # Stop processing
                
        if new_pos[0] < 0 or new_pos[0] + self.width > self.parent.width:
            # Side wall collision
            self.velocity.x = -self.velocity.x * bounce_factor
            new_pos = (max(0, min(new_pos[0], self.parent.width - self.width)), new_pos[1])
            self.bounce_count += 1

        # 7. Check Wall collision with destructible walls
        # Horizontal movement
        self.x = new_pos[0]

        for wall in walls:
            # If wall is destructible
            if hasattr(wall, "blocks"):
                for block in wall.blocks[:]:  # copy to avoid modifying while iterating
                    if self.collide_widget(block):
                        # Destroy the block at ball's position
                        wall.destroy_at(self.center, radius=15)
                        
                        # Bounce horizontally
                        self.x = old_x
                        self.velocity.x *= -bounce_factor
                        self.bounce_count += 1
                        break  # only one block per frame

        # Vertical movement
        self.y = new_pos[1]

        for wall in walls:
            if hasattr(wall, "blocks"):
                for block in wall.blocks[:]:
                    if self.collide_widget(block):
                        # Destroy the block at ball's position
                        wall.destroy_at(self.center, radius=15)
                        
                        # Bounce vertically
                        self.y = old_y
                        self.velocity.y *= -bounce_factor
                        
                        # Optional: stop if settling
                        if abs(self.velocity.y) < 1:
                            self.velocity.y = 0
                        
                        self.bounce_count += 1
                        break

        # Re-calculate new_pos based on corrected collision results
        new_pos = self.x, self.y
                
        # 6. Check Termination Conditions (Two-Bounce Limit)
        if self.bounce_count >= self.bounce_limit:
            self.velocity = Vector(0, 0)
            self.fired = False # <--- MUST BE SET TO FALSE
            return # Stop processing

        # 7. Apply new position
        self.pos = new_pos
        
        # 8. Update ball color
        self.draw_gradient() 
        
    def draw_gradient(self):
        """
        Draws the dynamic, animated gradient inside the ball.
        (Logic kept from user's original input)
        """
        self.gradient_group.clear()
        
        speed = self.velocity.length()
        norm_speed = min(speed / 25.0, 1.0)

        if norm_speed < 0.3:
            t = norm_speed / 0.3
            interp_r, interp_g, interp_b = 0.0, 1.0 - t, t # Green (1.0) -> Blue (1.0)
        else:
            t = (norm_speed - 0.3) / 0.7
            interp_r, interp_g, interp_b = t, 0.0, 1.0 - t

        num_ellipses = 40

        for i in range(num_ellipses, 0, -1):
            progress = i / num_ellipses
            animation_factor = math.sin(self.time_offset * 5 + progress * 15) * 0.2 + 1.0
            size_factor = progress * animation_factor
            
            r, g, b = interp_r * size_factor, interp_g * size_factor, interp_b * size_factor
            
            ring_size = (self.width * size_factor, self.height * size_factor)
            ring_pos = (
                self.center_x - ring_size[0] / 2.0,
                self.center_y - ring_size[1] / 2.0
            )

            self.gradient_group.add(Color(r, g, b, 1.0))
            self.gradient_group.add(Ellipse(pos=ring_pos, size=ring_size))


    def move(self, bounce_factor, walls):
        """
        Moves the ball and handles bouncing from walls and window edges.
        If the ball settles (velocity near zero at the bottom), stop firing.
        """
        if not self.parent: return
    
        old_x, old_y = self.x, self.y
    
        # ---- Move X ----
        self.x += self.velocity.x
        collided_x = any(self.collide_widget(w) for w in walls)
        if collided_x:
            self.x = old_x
            self.velocity.x *= -bounce_factor
            self.bounce_count += 1
    
        # ---- Move Y ----
        self.y += self.velocity.y
        collided_y = any(self.collide_widget(w) for w in walls)
        if collided_y:
            self.y = old_y
            self.velocity.y *= -bounce_factor
            self.bounce_count += 1
    
        # ---- Window bounds ----
        if self.x < 0:
            self.x = 0
            self.velocity.x *= -bounce_factor
        elif self.right > self.parent.width:
            self.right = self.parent.width
            self.velocity.x *= -bounce_factor
    
        if self.y < 50: # Assuming 50 is the ground wall height
            self.y = 50 
            self.velocity.y *= -bounce_factor
            
            # --- Bounce Logic ---
            self.bounce_count += 1  # <--- Increment Bounce Count
            
            # Stop if ball settles (existing logic)
            if abs(self.velocity.y) < 1 and abs(self.velocity.x) < 1:
                 self.velocity = Vector(0, 0)
                 self.fired = False 
                 
        # --- NEW: Two-Bounce Limit ---
        if self.bounce_count >= 2:
            self.velocity = Vector(0, 0)
            self.fired = False  # Signal end of turn and removal
            return