import tkinter as tk
from tkinter import messagebox
import random

class CarParkingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Car Parking Game")
        self.root.geometry("800x600")
        
        # Game canvas
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='gray')
        self.canvas.pack()
        
        # Game variables
        self.car_width = 40
        self.car_height = 60
        self.car_x = 400
        self.car_y = 500
        self.car_angle = 0
        self.speed = 0
        self.steering = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        
        # Create parking spots
        self.parking_spots = []
        self.create_parking_lot()
        
        # Create car
        self.car = self.create_car()
        
        # Create obstacles
        self.obstacles = []
        self.create_obstacles()
        
        # Bind controls
        self.root.bind('<Left>', self.turn_left)
        self.root.bind('<Right>', self.turn_right)
        self.root.bind('<Up>', self.accelerate)
        self.root.bind('<Down>', self.brake)
        self.root.bind('<space>', self.reset_level)
        
        # Start game loop
        self.update_game()
        
    def create_car(self):
        car = self.canvas.create_rectangle(
            self.car_x - self.car_width/2,
            self.car_y - self.car_height/2,
            self.car_x + self.car_width/2,
            self.car_y + self.car_height/2,
            fill='blue',
            tags='car'
        )
        # Add direction indicator
        self.direction = self.canvas.create_line(
            self.car_x,
            self.car_y,
            self.car_x,
            self.car_y - self.car_height/2,
            fill='yellow',
            width=2
        )
        return car
        
    def create_parking_lot(self):
        # Create parking spots
        spot_positions = [
            (100, 100), (300, 100), (500, 100),
            (100, 300), (300, 300), (500, 300)
        ]
        for x, y in spot_positions:
            spot = self.canvas.create_rectangle(
                x - 30, y - 45,
                x + 30, y + 45,
                outline='white',
                width=2
            )
            self.parking_spots.append(spot)
            
        # Highlight target parking spot
        self.target_spot = random.choice(self.parking_spots)
        self.canvas.itemconfig(self.target_spot, outline='green', width=3)
        
    def create_obstacles(self):
        obstacle_positions = [
            (200, 200), (400, 200), (600, 200),
            (200, 400), (400, 400), (600, 400)
        ]
        for x, y in obstacle_positions:
            if random.random() < 0.5:  # 50% chance to place obstacle
                obstacle = self.canvas.create_rectangle(
                    x - 20, y - 20,
                    x + 20, y + 20,
                    fill='red'
                )
                self.obstacles.append(obstacle)
                
    def turn_left(self, event):
        if not self.game_over:
            self.steering = -3
            
    def turn_right(self, event):
        if not self.game_over:
            self.steering = 3
            
    def accelerate(self, event):
        if not self.game_over:
            self.speed = min(self.speed + 0.5, 5)
            
    def brake(self, event):
        if not self.game_over:
            self.speed = max(self.speed - 0.5, -2)
            
    def update_car_position(self):
        # Update angle
        self.car_angle += self.steering
        
        # Calculate new position
        rad_angle = self.car_angle * 3.14159 / 180
        dx = self.speed * -1 * (rad_angle)
        dy = self.speed * -1
        
        # Update position
        self.car_x += dx
        self.car_y += dy
        
        # Keep car in bounds
        self.car_x = max(self.car_width/2, min(800 - self.car_width/2, self.car_x))
        self.car_y = max(self.car_height/2, min(600 - self.car_height/2, self.car_y))
        
        # Move car
        self.canvas.coords(
            self.car,
            self.car_x - self.car_width/2,
            self.car_y - self.car_height/2,
            self.car_x + self.car_width/2,
            self.car_y + self.car_height/2
        )
        
        # Update direction indicator
        self.canvas.coords(
            self.direction,
            self.car_x,
            self.car_y,
            self.car_x + 20 * (rad_angle),
            self.car_y - 20
        )
        
    def check_collision(self):
        car_coords = self.canvas.bbox(self.car)
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            obs_coords = self.canvas.bbox(obstacle)
            if self.check_overlap(car_coords, obs_coords):
                self.game_over = True
                self.show_game_over("Crashed!")
                return True
                
        return False
        
    def check_parking(self):
        car_coords = self.canvas.bbox(self.car)
        target_coords = self.canvas.bbox(self.target_spot)
        
        if self.check_overlap(car_coords, target_coords) and abs(self.speed) < 0.1:
            self.score += 100
            self.level += 1
            self.next_level()
            
    def check_overlap(self, coords1, coords2):
        return not (coords1[2] < coords2[0] or
                   coords1[0] > coords2[2] or
                   coords1[3] < coords2[1] or
                   coords1[1] > coords2[3])
                   
    def next_level(self):
        self.canvas.delete('all')
        self.obstacles.clear()
        self.parking_spots.clear()
        
        # Reset car position
        self.car_x = 400
        self.car_y = 500
        self.car_angle = 0
        self.speed = 0
        self.steering = 0
        
        # Create new level
        self.create_parking_lot()
        self.car = self.create_car()
        self.create_obstacles()
        
    def show_game_over(self, message):
        self.canvas.create_text(
            400, 300,
            text=f"{message}\nScore: {self.score}\nPress Space to restart",
            font=('Arial', 20),
            fill='white'
        )
        
    def reset_level(self, event):
        if self.game_over:
            self.game_over = False
            self.score = 0
            self.level = 1
            self.next_level()
            
    def update_game(self):
        if not self.game_over:
            self.update_car_position()
            self.check_collision()
            self.check_parking()
            
            # Update score display
            self.canvas.delete('score')
            self.canvas.create_text(
                700, 50,
                text=f"Score: {self.score}\nLevel: {self.level}",
                font=('Arial', 16),
                fill='white',
                tags='score'
            )
            
            # Gradually reduce steering and speed
            self.steering *= 0.95
            self.speed *= 0.99
            
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CarParkingGame()
    game.run()

"""

- Save the code as car_parking_game.py
- Run the file using Python
- Controls:
- Arrow Up: Accelerate
- Arrow Down: Brake/Reverse
- Arrow Left: Turn Left
- Arrow Right: Turn Right
- Space: Restart game when game over


"""