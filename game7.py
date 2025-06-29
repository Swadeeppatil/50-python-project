import tkinter as tk
from tkinter import messagebox
import random
import time

class CarRacingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Car Racing Game")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Game variables
        self.score = 0
        self.game_speed = 10
        self.game_over = False
        self.pause = False
        
        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='gray')
        self.canvas.pack()
        
        # Road lines
        self.lines = []
        self.create_road_lines()
        
        # Player car
        self.player_car = self.canvas.create_rectangle(350, 500, 450, 550, fill='blue')
        
        # Enemy cars
        self.enemy_cars = []
        self.create_enemy_car()
        
        # Score label
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=('Arial', 20))
        self.score_label.place(x=10, y=10)
        
        # Controls
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<space>', self.toggle_pause)
        
        # Start game
        self.update_game()
        
    def create_road_lines(self):
        for i in range(5):
            line = self.canvas.create_rectangle(390, i * 150, 410, (i * 150) + 100, fill='white')
            self.lines.append(line)
            
    def create_enemy_car(self):
        colors = ['red', 'green', 'yellow', 'purple', 'orange']
        x = random.randint(200, 600)
        enemy = self.canvas.create_rectangle(x, -50, x+100, 0, fill=random.choice(colors))
        self.enemy_cars.append(enemy)
        
    def move_left(self, event):
        if not self.pause and not self.game_over:
            pos = self.canvas.coords(self.player_car)
            if pos[0] > 0:
                self.canvas.move(self.player_car, -20, 0)
                
    def move_right(self, event):
        if not self.pause and not self.game_over:
            pos = self.canvas.coords(self.player_car)
            if pos[2] < 800:
                self.canvas.move(self.player_car, 20, 0)
                
    def toggle_pause(self, event):
        self.pause = not self.pause
        
    def move_lines(self):
        for line in self.lines:
            self.canvas.move(line, 0, self.game_speed)
            pos = self.canvas.coords(line)
            if pos[1] >= 600:
                self.canvas.moveto(line, 390, -100)
                
    def move_enemy_cars(self):
        for car in self.enemy_cars:
            self.canvas.move(car, 0, self.game_speed)
            pos = self.canvas.coords(car)
            if pos[1] >= 600:
                self.canvas.delete(car)
                self.enemy_cars.remove(car)
                self.score += 10
                self.score_label.config(text=f"Score: {self.score}")
                if self.score % 50 == 0:
                    self.game_speed += 1
                    
    def check_collision(self):
        player_pos = self.canvas.coords(self.player_car)
        for car in self.enemy_cars:
            car_pos = self.canvas.coords(car)
            if self.detect_collision(player_pos, car_pos):
                self.game_over = True
                self.show_game_over()
                
    def detect_collision(self, player, enemy):
        if player[0] < enemy[2] and player[2] > enemy[0]:
            if player[1] < enemy[3] and player[3] > enemy[1]:
                return True
        return False
    
    def show_game_over(self):
        self.canvas.create_text(400, 300, text="Game Over!", font=('Arial', 30), fill='red')
        if messagebox.askyesno("Game Over", f"Your score: {self.score}\nPlay again?"):
            self.reset_game()
        else:
            self.root.quit()
            
    def reset_game(self):
        self.score = 0
        self.game_speed = 10
        self.game_over = False
        self.score_label.config(text=f"Score: {self.score}")
        
        # Clear enemy cars
        for car in self.enemy_cars:
            self.canvas.delete(car)
        self.enemy_cars.clear()
        
        # Reset player position
        self.canvas.coords(self.player_car, 350, 500, 450, 550)
        
    def update_game(self):
        if not self.pause and not self.game_over:
            self.move_lines()
            self.move_enemy_cars()
            self.check_collision()
            
            # Create new enemy cars
            if len(self.enemy_cars) < 3:
                if random.random() < 0.02:
                    self.create_enemy_car()
                    
        self.root.after(50, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CarRacingGame()
    game.run()