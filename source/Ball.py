import math
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.graphics import Ellipse, Color, InstructionGroup
from kivy.uix.label import Label


class Ball(Widget):
    """
    The main player ball with dynamic, animated graphics.
    The graphics are a pulsating gradient that changes color based on speed.
    """
    velocity = Vector(0, 0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Draw the base ball
        with self.canvas:
            self.outer_color = Color(0, 0, 1, 1)  # Blue border
            self.outer_ellipse = Ellipse(pos=self.pos, size=self.size)

        # Debug label
        self.debug_label = Label(text="Debug", pos=(10, 10))
        self.add_widget(self.debug_label)

        # InstructionGroup for the gradient to allow easy clearing and redrawing
        self.gradient_group = InstructionGroup()
        self.canvas.add(self.gradient_group)

        # Time offset for the pulsating animation
        self.time_offset = 0.0

        # Keep graphics synced with widget position and size
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        """Updates the position and size of the outer ellipse."""
        self.outer_ellipse.pos = self.pos
        self.outer_ellipse.size = self.size

    def update(self, dt, walls, bounce_factor=0.5):
        """Main update function called by the game loop."""
        self.time_offset += dt
        self.move(bounce_factor, walls)
        self.draw_gradient()

    def draw_gradient(self):
        """
        Draws the dynamic, animated gradient inside the ball.
        The animation is time-based, and the color changes based on speed
        from Green -> Blue -> Red.
        """
        # Clear previous gradient instructions
        self.gradient_group.clear()

        # Ball speed to color mapping
        speed = self.velocity.length()
        # Normalize speed to a 0.0 to 1.0 range, capping it to prevent extreme values.
        norm_speed = min(speed / 30.0, 1.0)

        # Interpolate the base color based on speed: Green -> Blue -> Red.
        if norm_speed < 0.5:
            # Transition from Green (0, 1, 0) to Blue (0, 0, 1).
            t = norm_speed / 0.5
            interp_r = 0.0
            interp_g = 1.0 - t
            interp_b = t
        else:
            # Transition from Blue (0, 0, 1) to Red (1, 0, 0).
            t = (norm_speed - 0.5) / 0.5
            interp_r = t
            interp_g = 0.0
            interp_b = 1.0 - t

        # Number of ellipses to draw to create the gradient effect.
        num_ellipses = 40

        # Iterate from the largest ellipse (outermost) to the smallest (innermost).
        for i in range(num_ellipses, 0, -1):
            # Calculate the progress of this ellipse from 0 to 1 (outer to inner).
            progress = i / num_ellipses

            # The size of each ring is based on its progress and a time-modulated factor.
            # The sin function creates the pulsing effect.
            animation_factor = math.sin(self.time_offset * 5 + progress * 15) * 0.2 + 1.0
            size_factor = progress * animation_factor
            
            # The color of each individual ellipse in the gradient.
            # We transition from the interpolated color at the edge to black at the center.
            r = interp_r * size_factor
            g = interp_g * size_factor
            b = interp_b * size_factor
            
            # The size of each ellipse scales down towards the center.
            ring_size = (self.width * size_factor, self.height * size_factor)
            
            # Center the ellipse's position.
            ring_pos = (
                self.center_x - ring_size[0] / 2.0,
                self.center_y - ring_size[1] / 2.0
            )

            # Add the new color and ellipse instructions to the canvas.
            color_instr = Color(r, g, b, 1.0)
            ellipse_instr = Ellipse(pos=ring_pos, size=ring_size)
            self.gradient_group.add(color_instr)
            self.gradient_group.add(ellipse_instr)

    def move(self, bounce_factor, walls):
        """
        Moves the ball and handles bouncing from walls and window edges.
        Uses rollback to the last valid position instead of snapping to wall edges.
        """
        if not self.parent:
            return
    
        # Save old position before moving
        old_x, old_y = self.x, self.y
    
        # ---- Move X ----
        self.x += self.velocity.x
        collided_x = any(self.collide_widget(w) for w in walls)
        if collided_x:
            # Roll back and bounce
            self.x = old_x
            self.velocity.x *= -bounce_factor
    
        # ---- Move Y ----
        self.y += self.velocity.y
        collided_y = any(self.collide_widget(w) for w in walls)
        if collided_y:
            # Roll back and bounce
            self.y = old_y
            self.velocity.y *= -bounce_factor
    
        # ---- Window bounds ----
        if self.x < 0:
            self.x = 0
            self.velocity.x *= -bounce_factor
        elif self.right > self.parent.width:
            self.right = self.parent.width
            self.velocity.x *= -bounce_factor
    
        if self.y < 0:
            self.y = 0
            self.velocity.y *= -bounce_factor
        elif self.top > self.parent.height:
            self.top = self.parent.height
            self.velocity.y *= -bounce_factor
    
