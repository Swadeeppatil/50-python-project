import tkinter as tk
import random
import math

class HillClimbRacing:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hill Climb Racing")
        self.root.geometry("1000x600")
        
        # Game canvas
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg='skyblue')
        self.canvas.pack()
        
        # Game variables
        self.car_x = 100
        self.car_y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        self.fuel = 100
        self.score = 0
        self.game_over = False
        
        # Terrain generation
        self.terrain_points = []
        self.generate_terrain()
        
        # Create car
        self.car = self.create_car()
        self.wheels = self.create_wheels()
        
        # Controls
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Up>', self.accelerate)
        self.root.bind('<space>', self.restart_game)
        
        # Start game loop
        self.update_game()
        
    def create_car(self):
        car_body = self.canvas.create_polygon(
            self.car_x, self.car_y,
            self.car_x + 80, self.car_y,
            self.car_x + 80, self.car_y - 30,
            self.car_x + 60, self.car_y - 30,
            self.car_x + 40, self.car_y - 45,
            self.car_x + 20, self.car_y - 45,
            self.car_x, self.car_y - 30,
            fill='red'
        )
        return car_body
        
    def create_wheels(self):
        wheel1 = self.canvas.create_oval(
            self.car_x + 10, self.car_y + 5,
            self.car_x + 30, self.car_y + 25,
            fill='black'
        )
        wheel2 = self.canvas.create_oval(
            self.car_x + 50, self.car_y + 5,
            self.car_x + 70, self.car_y + 25,
            fill='black'
        )
        return [wheel1, wheel2]
        
    def generate_terrain(self):
        x = 0
        y = 400
        while x < 2000:
            y += random.randint(-30, 30)
            y = min(550, max(200, y))
            self.terrain_points.append((x, y))
            x += 20
        
        # Create terrain on canvas
        self.terrain = self.canvas.create_line(
            self.terrain_points,
            fill='green',
            width=3
        )
        
    def move_left(self, event):
        if not self.game_over and self.fuel > 0:
            self.velocity_x = max(-5, self.velocity_x - 0.5)
            self.fuel -= 0.1
            
    def move_right(self, event):
        if not self.game_over and self.fuel > 0:
            self.velocity_x = min(5, self.velocity_x + 0.5)
            self.fuel -= 0.1
            
    def accelerate(self, event):
        if not self.game_over and self.fuel > 0:
            self.velocity_y = -5
            self.fuel -= 0.2
            
    def update_car_position(self):
        # Apply gravity
        self.velocity_y += 0.2
        
        # Update position
        self.car_x += self.velocity_x
        self.car_y += self.velocity_y
        
        # Get terrain height at car position
        terrain_y = self.get_terrain_height(self.car_x)
        
        # Check collision with terrain
        if self.car_y > terrain_y - 20:
            self.car_y = terrain_y - 20
            self.velocity_y = 0
            
        # Move car and wheels
        self.canvas.moveto(self.car, self.car_x, self.car_y)
        self.canvas.moveto(self.wheels[0], self.car_x + 10, self.car_y + 5)
        self.canvas.moveto(self.wheels[1], self.car_x + 50, self.car_y + 5)
        
        # Rotate wheels
        self.rotate_wheels()
        
    def rotate_wheels(self):
        angle = math.degrees(self.velocity_x / 2)
        for wheel in self.wheels:
            x1, y1, x2, y2 = self.canvas.coords(wheel)
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            self.canvas.delete(wheel)
            wheel = self.canvas.create_oval(x1, y1, x2, y2, fill='black')
            
    def get_terrain_height(self, x):
        for i in range(len(self.terrain_points) - 1):
            x1, y1 = self.terrain_points[i]
            x2, y2 = self.terrain_points[i + 1]
            if x1 <= x <= x2:
                # Linear interpolation
                ratio = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * ratio
        return 400
        
    def check_game_over(self):
        if self.fuel <= 0 or self.car_y > 600:
            self.game_over = True
            self.canvas.create_text(
                500, 300,
                text=f"Game Over!\nScore: {int(self.score)}\nPress Space to restart",
                font=('Arial', 24),
                fill='red'
            )
            
    def restart_game(self, event):
        if self.game_over:
            self.canvas.delete('all')
            self.__init__()
            
    def update_game(self):
        if not self.game_over:
            self.update_car_position()
            
            # Update score and fuel display
            self.score += self.velocity_x * 0.1
            self.canvas.delete('status')
            self.canvas.create_text(
                100, 50,
                text=f"Score: {int(self.score)}\nFuel: {int(self.fuel)}",
                font=('Arial', 16),
                fill='black',
                tags='status'
            )
            
            # Scroll terrain
            self.canvas.xview_scroll(int(self.velocity_x), 'units')
            
            # Check game over conditions
            self.check_game_over()
            
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = HillClimbRacing()
    game.run()