import tkinter as tk
import random
import math
class BubbleShooter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bubble Shooter")
        
        self.canvas = tk.Canvas(self.root, width=500, height=600, bg='black')
        self.canvas.pack()
        self.score = 0
        self.bubbles = []
        self.bullet = None
        self.bullet_angle = 90
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple']
        self.shooter = self.canvas.create_rectangle(240, 550, 260, 570, fill='white')
        self.score_text = self.canvas.create_text(50, 20, text="Score: 0", fill='white')
        self.create_bubbles()
        self.canvas.bind('<Motion>', self.aim)
        self.canvas.bind('<Button-1>', self.shoot)
        self.update_game()
    def create_bubbles(self):
        for row in range(5):
            for col in range(10):
                x = col * 50 + 25
                y = row * 30 + 25
                color = random.choice(self.colors)
                bubble = self.canvas.create_oval(x-15, y-15, x+15, y+15, fill=color)
                self.bubbles.append({'id': bubble, 'color': color})          
    def aim(self, event):
        if not self.bullet:
            dx = event.x - 250
            dy = 560 - event.y
            self.bullet_angle = math.degrees(math.atan2(dy, dx))    
    def shoot(self, event):
        if not self.bullet:
            angle_rad = math.radians(self.bullet_angle)
            color = random.choice(self.colors)
            self.bullet = {
                'id': self.canvas.create_oval(235, 535, 265, 565, fill=color),
                'dx': math.cos(angle_rad) * 10,
                'dy': -math.sin(angle_rad) * 10,
                'color': color
            }      
    def update_game(self):
        if self.bullet:
            self.canvas.move(self.bullet['id'], self.bullet['dx'], self.bullet['dy'])
            pos = self.canvas.coords(self.bullet['id'])
            if pos[0] <= 0 or pos[2] >= 500:
                self.bullet['dx'] *= -1
            if pos[1] <= 0:
                self.canvas.delete(self.bullet['id'])
                self.bullet = None
            for bubble in self.bubbles[:]:
                bubble_pos = self.canvas.coords(bubble['id'])
                if self.check_collision(pos, bubble_pos):
                    if bubble['color'] == self.bullet['color']:
                        self.canvas.delete(bubble['id'])
                        self.bubbles.remove(bubble)
                        self.score += 10
                        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    self.canvas.delete(self.bullet['id'])
                    self.bullet = None
                    break          
        if len(self.bubbles) == 0:
            self.canvas.create_text(250, 300, text="You Win!", fill='white', font=('Arial', 30))   
        self.root.after(16, self.update_game)  
    def check_collision(self, pos1, pos2):
        x1 = (pos1[0] + pos1[2]) / 2
        y1 = (pos1[1] + pos1[3]) / 2
        x2 = (pos2[0] + pos2[2]) / 2
        y2 = (pos2[1] + pos2[3]) / 2
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return distance < 30  
    def run(self):
        self.root.mainloop()
if __name__ == "__main__":
    game = BubbleShooter()
    game.run()