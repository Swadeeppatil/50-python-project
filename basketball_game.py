import tkinter as tk
import random
import math

class BasketballGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Basketball Game")
        self.root.geometry("800x600")
        
        # Game variables
        self.score = 0
        self.time_left = 60
        self.ball_in_hand = True
        self.power = 0
        self.angle = 45
        self.game_over = False
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='lightblue')
        self.canvas.pack()
        
        # Create game elements
        self.create_court()
        self.create_basket()
        self.create_ball()
        self.create_player()
        self.create_scoreboard()
        
        # Bind controls
        self.setup_controls()
        
        # Start game loop
        self.update_game()
        
    def create_court(self):
        # Draw court floor
        self.canvas.create_rectangle(0, 500, 800, 600, fill='brown')
        # Draw court lines
        self.canvas.create_line(0, 500, 800, 500, fill='white', width=2)
        
    def create_basket(self):
        # Draw backboard
        self.canvas.create_rectangle(700, 200, 720, 300, fill='white')
        # Draw rim
        self.rim = self.canvas.create_rectangle(670, 280, 700, 285, fill='red')
        # Draw net (simplified)
        for i in range(5):
            self.canvas.create_line(670+i*6, 285, 670+i*6, 320, fill='white')
            
    def create_ball(self):
        self.ball = self.canvas.create_oval(100, 450, 120, 470, fill='orange')
        self.ball_x = 110
        self.ball_y = 460
        self.ball_dx = 0
        self.ball_dy = 0
        
    def create_player(self):
        # Simple player representation
        self.player = self.canvas.create_rectangle(80, 430, 100, 500, fill='blue')
        
    def create_scoreboard(self):
        self.score_text = self.canvas.create_text(50, 30, text=f"Score: {self.score}", 
                                                font=('Arial', 20), fill='black')
        self.time_text = self.canvas.create_text(50, 60, text=f"Time: {self.time_left}", 
                                               font=('Arial', 20), fill='black')
        self.power_bar = self.canvas.create_rectangle(20, 100, 40, 300, outline='black')
        self.power_fill = self.canvas.create_rectangle(20, 300, 40, 300, fill='red')
        
    def setup_controls(self):
        self.root.bind('<Left>', lambda e: self.move_player(-10))
        self.root.bind('<Right>', lambda e: self.move_player(10))
        self.root.bind('<space>', self.charge_shot)
        self.root.bind('<KeyRelease-space>', self.shoot_ball)
        
    def move_player(self, dx):
        if not self.game_over:
            pos = self.canvas.coords(self.player)
            if 0 <= pos[0] + dx <= 700:
                self.canvas.move(self.player, dx, 0)
                if self.ball_in_hand:
                    self.canvas.move(self.ball, dx, 0)
                    self.ball_x += dx
                    
    def charge_shot(self, event):
        if self.ball_in_hand and not self.game_over:
            self.power = min(self.power + 2, 100)
            self.canvas.coords(self.power_fill, 20, 300-self.power*2, 40, 300)
            
    def shoot_ball(self, event):
        if self.ball_in_hand and not self.game_over and self.power > 0:
            self.ball_in_hand = False
            angle_rad = math.radians(self.angle)
            self.ball_dx = self.power * math.cos(angle_rad) * 0.3
            self.ball_dy = -self.power * math.sin(angle_rad) * 0.3
            self.power = 0
            self.canvas.coords(self.power_fill, 20, 300, 40, 300)
            
    def update_ball_position(self):
        if not self.ball_in_hand:
            # Apply gravity
            self.ball_dy += 0.5
            
            # Update position
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy
            
            # Update ball on canvas
            self.canvas.coords(self.ball, 
                             self.ball_x-10, self.ball_y-10,
                             self.ball_x+10, self.ball_y+10)
            
            # Check for scoring
            if (670 <= self.ball_x <= 700 and 
                270 <= self.ball_y <= 285 and 
                self.ball_dy > 0):
                self.score += 2
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                
            # Check for ball out of bounds or floor collision
            if self.ball_y > 460 or self.ball_x > 800 or self.ball_x < 0:
                self.reset_ball()
                
    def reset_ball(self):
        player_pos = self.canvas.coords(self.player)
        self.ball_x = player_pos[0] + 20
        self.ball_y = 460
        self.ball_dx = 0
        self.ball_dy = 0
        self.ball_in_hand = True
        self.canvas.coords(self.ball, 
                         self.ball_x-10, self.ball_y-10,
                         self.ball_x+10, self.ball_y+10)
        
    def update_time(self):
        if not self.game_over:
            self.time_left -= 1
            self.canvas.itemconfig(self.time_text, text=f"Time: {self.time_left}")
            
            if self.time_left <= 0:
                self.game_over = True
                self.show_game_over()
                
    def show_game_over(self):
        self.canvas.create_text(400, 300, 
                              text=f"Game Over!\nFinal Score: {self.score}", 
                              font=('Arial', 30), fill='red')
        
    def update_game(self):
        if not self.game_over:
            self.update_ball_position()
            
        if self.time_left > 0:
            self.root.after(1000, self.update_time)
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = BasketballGame()
    game.run()

"""
- Save as basketball_game.py
- Run the file
- Controls:
- Left/Right Arrow: Move player
- Space (Hold): Charge shot power
- Space (Release): Shoot ball
"""
