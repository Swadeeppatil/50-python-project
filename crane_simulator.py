import tkinter as tk
import math
import random

class CraneSimulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Heavy Loader Crane Simulator")
        self.root.geometry("1000x800")
        
        # Game variables
        self.score = 0
        self.time_left = 180  # 3 minutes
        self.game_over = False
        self.current_load = None
        self.loads_delivered = 0
        self.crane_angle = 0
        self.cable_length = 100
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=1000, height=700, bg='skyblue')
        self.canvas.pack(pady=10)
        
        # Create game elements
        self.create_crane()
        self.create_loads()
        self.create_targets()
        self.create_controls()
        self.create_scoreboard()
        
        # Start game loop
        self.update_game()
        
    def create_crane(self):
        # Base
        self.crane_base = self.canvas.create_rectangle(450, 50, 550, 100, fill='gray')
        # Tower
        self.crane_tower = self.canvas.create_rectangle(480, 50, 520, 200, fill='red')
        # Arm
        self.crane_arm = self.canvas.create_line(500, 200, 500, 200, fill='black', width=5)
        # Hook
        self.crane_hook = self.canvas.create_rectangle(495, 300, 505, 310, fill='yellow')
        self.update_crane_position()
        
    def create_loads(self):
        self.loads = []
        self.load_positions = [(100, 600), (200, 600), (300, 600)]
        colors = ['blue', 'green', 'orange']
        
        for pos, color in zip(self.load_positions, colors):
            load = self.canvas.create_rectangle(
                pos[0]-20, pos[1]-20, pos[0]+20, pos[1]+20,
                fill=color, tags='load'
            )
            self.loads.append(load)
            
    def create_targets(self):
        self.targets = []
        self.target_positions = [(700, 600), (800, 600), (900, 600)]
        
        for pos in self.target_positions:
            target = self.canvas.create_rectangle(
                pos[0]-25, pos[1]-25, pos[0]+25, pos[1]+25,
                outline='red', width=2
            )
            self.targets.append(target)
            
    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill='x', padx=10)
        
        tk.Label(control_frame, text="Controls:", font=('Arial', 12)).pack(side='left')
        tk.Label(control_frame, 
                text="Left/Right: Rotate | Up/Down: Cable | Space: Grab/Release", 
                font=('Arial', 12)).pack(side='left', padx=10)
                
    def create_scoreboard(self):
        self.score_label = self.canvas.create_text(
            50, 30, text=f"Score: {self.score}", 
            font=('Arial', 16), fill='black'
        )
        self.time_label = self.canvas.create_text(
            50, 60, text=f"Time: {self.time_left}s", 
            font=('Arial', 16), fill='black'
        )
        
    def update_crane_position(self):
        # Update arm position
        arm_x = 500 + math.cos(math.radians(self.crane_angle)) * 300
        arm_y = 200 + math.sin(math.radians(self.crane_angle)) * 300
        self.canvas.coords(self.crane_arm, 500, 200, arm_x, arm_y)
        
        # Update hook position
        hook_x = 500 + math.cos(math.radians(self.crane_angle)) * self.cable_length
        hook_y = 200 + math.sin(math.radians(self.crane_angle)) * self.cable_length
        self.canvas.coords(self.crane_hook, 
                         hook_x-5, hook_y-5, hook_x+5, hook_y+5)
                         
        # Update carried load if any
        if self.current_load:
            self.canvas.coords(self.current_load,
                             hook_x-20, hook_y+5,
                             hook_x+20, hook_y+45)
            
    def rotate_crane(self, direction):
        if not self.game_over:
            self.crane_angle += direction * 2
            self.crane_angle = max(-80, min(80, self.crane_angle))
            self.update_crane_position()
            
    def adjust_cable(self, direction):
        if not self.game_over:
            self.cable_length += direction * 10
            self.cable_length = max(100, min(500, self.cable_length))
            self.update_crane_position()
            
    def toggle_grab(self):
        if self.game_over:
            return
            
        hook_pos = self.canvas.coords(self.crane_hook)
        hook_center = ((hook_pos[0] + hook_pos[2])/2, 
                      (hook_pos[1] + hook_pos[3])/2)
        
        if not self.current_load:
            # Try to grab a load
            for load in self.loads:
                if load in self.canvas.find_all():  # Check if load still exists
                    load_pos = self.canvas.coords(load)
                    if self.check_proximity(hook_center, load_pos):
                        self.current_load = load
                        break
        else:
            # Try to drop the load
            for i, target in enumerate(self.targets):
                target_pos = self.canvas.coords(target)
                load_pos = self.canvas.coords(self.current_load)
                if self.check_proximity((load_pos[0]+20, load_pos[3]), target_pos):
                    self.canvas.delete(self.current_load)
                    self.loads.remove(self.current_load)
                    self.current_load = None
                    self.score += 100
                    self.loads_delivered += 1
                    
                    # Create new load if all delivered
                    if self.loads_delivered % 3 == 0:
                        self.create_loads()
                    break
            else:
                # Drop load if not over target
                load_pos = self.canvas.coords(self.current_load)
                self.canvas.coords(self.current_load,
                                 load_pos[0], load_pos[1],
                                 load_pos[2], load_pos[3])
                self.current_load = None
                
    def check_proximity(self, pos1, pos2):
        distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return distance < 50
        
    def update_time(self):
        if not self.game_over:
            self.time_left -= 1
            self.canvas.itemconfig(self.time_label, text=f"Time: {self.time_left}s")
            
            if self.time_left <= 0:
                self.game_over = True
                self.show_game_over()
                
    def show_game_over(self):
        self.canvas.create_text(
            500, 350,
            text=f"Game Over!\nFinal Score: {self.score}\nLoads Delivered: {self.loads_delivered}",
            font=('Arial', 24), fill='red',
            justify='center'
        )
        
    def update_game(self):
        if not self.game_over:
            self.canvas.itemconfig(self.score_label, text=f"Score: {self.score}")
            
        self.root.after(1000, self.update_time)
        self.root.after(16, self.update_game)
        
    def setup_controls(self):
        self.root.bind('<Left>', lambda e: self.rotate_crane(-1))
        self.root.bind('<Right>', lambda e: self.rotate_crane(1))
        self.root.bind('<Up>', lambda e: self.adjust_cable(-1))
        self.root.bind('<Down>', lambda e: self.adjust_cable(1))
        self.root.bind('<space>', lambda e: self.toggle_grab())
        
    def run(self):
        self.setup_controls()
        self.root.mainloop()

if __name__ == "__main__":
    game = CraneSimulator()
    game.run()

"""
o play the game:

1. Save as crane_simulator.py
2. Run the file
3. Controls:
   - Left/Right Arrow: Rotate crane
   - Up/Down Arrow: Adjust cable length
   - Space: Grab/Release loads
Features:

- Rotating crane arm
- Adjustable cable length
- Load picking and placing
- Score tracking
- Time limit
- Multiple targets
- Physics-based movement
- Visual feedback
- Continuous gameplay
- Progressive difficulty
Try to move as many loads as possible to their target locations before time runs out! The game gets more challenging as you progress.
"""
