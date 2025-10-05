import os

from kivy.uix.screenmanager import Screen
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock

class TankCarousel(Carousel):
    """
    A custom Carousel that dynamically scales tanks to simulate depth.
    The current tank is full size; tanks moving away shrink.
    """
    TANK_COLORS = ['red', 'yellow', 'green', 'blue']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.direction = 'right' # Set initial rotation direction
        self.bind(index=self.update_tank_size)
        
        # Create Image widgets for each tank
        for color in self.TANK_COLORS:
            base_path = os.path.join(os.path.dirname(__file__), "..", "resource", "tankImage", color)
            tank_path = os.path.join(base_path, "body.png")
            tank_path = os.path.abspath(tank_path) 

            tank_image = Image(
                source=tank_path,
                size_hint=(None, None),
                allow_stretch=True,
                keep_ratio=True
            )
            self.add_widget(tank_image)

        # Initial size update needs to happen after widgets are added
        Clock.schedule_once(lambda dt: self.update_tank_size(), 0)

    def update_tank_size(self, *args):
        """Scales the current widget to appear largest (in front)."""
        # Determine the target size for the main tank (e.g., 50% of the carousel height)
        target_height = self.height * 1.3 # enlarge size

        for i, tank in enumerate(self.slides):
            # Calculate the distance from the current index (wraps around)
            distance = min(abs(i - self.index), len(self.slides) - abs(i - self.index))
            
            # Use a scaling factor to simulate depth: 
            # 0 distance = 1.0 scale (full size)
            # 1 distance = 0.8 scale (slightly smaller)
            # 2 distance = 0.6 scale (smallest/furthest back)
            scale_factor = max(0.6, 1.0 - distance * 0.2) 
            
            # Apply the calculated size
            tank.height = target_height * scale_factor
            tank.width = tank.height * 1.5 # Assuming a 1.5:1 aspect ratio for the full.png
            tank.center_x = self.center_x + dp(20)
            tank.center_y = self.center_y - dp(120) # Lift slightly above the bottom bar

class TankSelectScreen(Screen):
    def on_enter(self, *args):
        # State tracking for selection
        self.player_turn = 1 # 1 or 2
        
        layout = BoxLayout(orientation='vertical')
        
        # 1. Title Label (Dynamic Text)
        self.title_label = Label(
            text=f"PLAYER 1: CHOOSE YOUR TANK", 
            size_hint=(1, 0.1), 
            font_size='32sp'
        )
        layout.add_widget(self.title_label)

        # 2. Tank Carousel
        self.carousel = TankCarousel(
            size_hint=(1, 0.7), 
            loop=True,
            scroll_timeout=500
        )
        self.carousel.bind(size=self.carousel.update_tank_size)
        layout.add_widget(self.carousel)
        
        # 3. Control Buttons/Selection
        control_bar = BoxLayout(size_hint=(1, 0.2), padding='10dp', spacing='20dp')
        
        prev_btn = Button(text="<", size_hint=(0.15, 1))
        prev_btn.bind(on_release=lambda x: self.carousel.load_previous())
        control_bar.add_widget(prev_btn)
        
        self.select_btn = Button(text="SELECT TANK", size_hint=(0.7, 1), font_size='24sp')
        self.select_btn.bind(on_release=self.handle_selection)
        control_bar.add_widget(self.select_btn)

        next_btn = Button(text=">", size_hint=(0.15, 1))
        next_btn.bind(on_release=lambda x: self.carousel.load_next())
        control_bar.add_widget(next_btn)

        layout.add_widget(control_bar)
        self.add_widget(layout)
        
    def handle_selection(self, *args):
        selected_index = self.carousel.index
        selected_color = self.carousel.TANK_COLORS[selected_index]
        
        if self.player_turn == 1:
            # Store P1 selection in the App (GameScreenManager)
            self.manager.p1_tank_color = selected_color
            
            # Prepare for P2 selection
            self.player_turn = 2
            self.title_label.text = "PLAYER 2: CHOOSE YOUR TANK"
            self.carousel.load_next() # Optionally move to next tank for P2
            
            print(f"✅ Player 1 selected: {selected_color}. Now P2 selects.")

        elif self.player_turn == 2:
            # Store P2 selection
            if selected_color == self.manager.p1_tank_color:
                # Prevent selecting the same tank, prompt user to choose again
                self.title_label.text = f"P2: Choose different tank! P1 chose {selected_color.upper()}"
                return
            
            self.manager.p2_tank_color = selected_color
            print(f"✅ Player 2 selected: {selected_color}. Starting game...")
            
            # Move to the game stage
            self.manager.current = "stage1_1"