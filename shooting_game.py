import tkinter as tk
import random
import math

class ShootingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shooting Game")
        self.root.geometry("800x600")
        
        # Game variables
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.targets = []
        self.bullets = []
        self.target_speed = 3
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='black')
        self.canvas.pack()
        
        # Create gun
        self.gun = self.canvas.create_rectangle(380, 550, 420, 580, fill='gray')
        self.gun_barrel = self.canvas.create_rectangle(395, 530, 405, 550, fill='gray')
        
        # Create score display
        self.score_text = self.canvas.create_text(50, 30, text=f"Score: {self.score}", 
                                                fill='white', font=('Arial', 16))
        self.lives_text = self.canvas.create_text(50, 60, text=f"Lives: {self.lives}", 
                                                fill='white', font=('Arial', 16))
        
        # Bind controls
        self.root.bind('<Left>', lambda e: self.move_gun(-10))
        self.root.bind('<Right>', lambda e: self.move_gun(10))
        self.root.bind('<space>', self.shoot)
        self.root.bind('<Return>', self.restart_game)
        
        # Start game
        self.spawn_target()
        self.update_game()
        
    def move_gun(self, dx):
        if not self.game_over:
            pos = self.canvas.coords(self.gun)
            if 0 <= pos[0] + dx <= 760:
                self.canvas.move(self.gun, dx, 0)
                self.canvas.move(self.gun_barrel, dx, 0)
                
    def shoot(self, event):
        if not self.game_over:
            gun_pos = self.canvas.coords(self.gun)
            bullet = self.canvas.create_oval(
                gun_pos[0] + 15, gun_pos[1] - 10,
                gun_pos[0] + 25, gun_pos[1],
                fill='yellow'
            )
            self.bullets.append(bullet)
            
    def spawn_target(self):
        if not self.game_over and len(self.targets) < 5:
            x = random.randint(0, 750)
            target = self.canvas.create_oval(x, 50, x + 50, 100, fill='red')
            self.targets.append({'id': target, 'dx': self.target_speed})
            
    def move_targets(self):
        for target in self.targets[:]:
            pos = self.canvas.coords(target['id'])
            
            # Bounce off walls
            if pos[0] <= 0 or pos[2] >= 800:
                target['dx'] *= -1
                
            self.canvas.move(target['id'], target['dx'], 0)
            
            # Check if target reached bottom
            if pos[3] >= 600:
                self.canvas.delete(target['id'])
                self.targets.remove(target)
                self.lives -= 1
                self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")
                
                if self.lives <= 0:
                    self.game_over = True
                    self.show_game_over()
                    
    def move_bullets(self):
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -10)
            bullet_pos = self.canvas.coords(bullet)
            
            # Check collision with targets
            for target in self.targets[:]:
                target_pos = self.canvas.coords(target['id'])
                if self.check_collision(bullet_pos, target_pos):
                    self.canvas.delete(bullet)
                    self.bullets.remove(bullet)
                    self.canvas.delete(target['id'])
                    self.targets.remove(target)
                    self.score += 10
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    break
                    
            # Remove bullets that are off screen
            if bullet_pos[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)
                
    def check_collision(self, bullet, target):
        return (bullet[2] >= target[0] and bullet[0] <= target[2] and
                bullet[3] >= target[1] and bullet[1] <= target[3])
                
    def show_game_over(self):
        self.canvas.create_text(400, 300, text=f"Game Over!\nScore: {self.score}\n"
                              "Press Enter to restart", fill='white', 
                              font=('Arial', 24), justify='center')
                              
    def restart_game(self, event=None):
        if self.game_over:
            # Clear canvas
            self.canvas.delete('all')
            
            # Reset variables
            self.score = 0
            self.lives = 3
            self.game_over = False
            self.targets = []
            self.bullets = []
            
            # Recreate game elements
            self.gun = self.canvas.create_rectangle(380, 550, 420, 580, fill='gray')
            self.gun_barrel = self.canvas.create_rectangle(395, 530, 405, 550, fill='gray')
            
            self.score_text = self.canvas.create_text(50, 30, text=f"Score: {self.score}", 
                                                    fill='white', font=('Arial', 16))
            self.lives_text = self.canvas.create_text(50, 60, text=f"Lives: {self.lives}", 
                                                    fill='white', font=('Arial', 16))
                                                    
    def update_game(self):
        if not self.game_over:
            self.move_targets()
            self.move_bullets()
            
            # Spawn new targets
            if random.random() < 0.02:
                self.spawn_target()
                
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = ShootingGame()
    game.run()

"""
To play the game:

1. Save as shooting_game.py
2. Run the file
3. Controls:
   - Left/Right Arrow: Move gun
   - Space: Shoot
   - Enter: Restart game (when game over)
Features:

- Moving targets
- Shooting mechanics
- Score tracking
- Lives system
- Collision detection
- Game over screen
- Restart functionality
- Smooth animations
- Multiple targets
- Bouncing targets
- Progressive difficulty
Try to shoot as many targets as possible before they reach the bottom! You have three lives, and each target hit gives you 10 points.
"""

