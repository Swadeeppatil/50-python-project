import tkinter as tk
import random
import math

class PUBGGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PUBG-Style Game")
        self.root.geometry("1000x800")
        
        # Game variables
        self.player_health = 100
        self.ammo = 30
        self.score = 0
        self.game_over = False
        self.enemies = []
        self.bullets = []
        self.items = []
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=1000, height=800, bg='darkgreen')
        self.canvas.pack()
        
        # Create player
        self.player = self.canvas.create_oval(480, 380, 520, 420, fill='blue', tags='player')
        self.player_direction = 0
        
        # Create obstacles
        self.create_obstacles()
        
        # Create status display
        self.status_text = self.canvas.create_text(
            100, 30, text=f"Health: {self.player_health} | Ammo: {self.ammo} | Score: {self.score}",
            fill='white', font=('Arial', 14)
        )
        
        # Bind controls
        self.setup_controls()
        
        # Start game
        self.spawn_enemies()
        self.spawn_items()
        self.update_game()
        
    def create_obstacles(self):
        for _ in range(10):
            x = random.randint(100, 900)
            y = random.randint(100, 700)
            size = random.randint(50, 100)
            self.canvas.create_rectangle(x, y, x+size, y+size, fill='gray')
            
    def setup_controls(self):
        self.root.bind('<Left>', lambda e: self.move_player(-5, 0))
        self.root.bind('<Right>', lambda e: self.move_player(5, 0))
        self.root.bind('<Up>', lambda e: self.move_player(0, -5))
        self.root.bind('<Down>', lambda e: self.move_player(0, 5))
        self.root.bind('<space>', self.shoot)
        self.root.bind('<Motion>', self.aim)
        self.root.bind('r', self.reload)
        
    def move_player(self, dx, dy):
        if not self.game_over:
            pos = self.canvas.coords(self.player)
            if (0 < pos[0] + dx < 980 and 0 < pos[2] + dx < 1000 and
                0 < pos[1] + dy < 780 and 0 < pos[3] + dy < 800):
                self.canvas.move(self.player, dx, dy)
                
    def aim(self, event):
        if not self.game_over:
            player_pos = self.canvas.coords(self.player)
            player_x = (player_pos[0] + player_pos[2]) / 2
            player_y = (player_pos[1] + player_pos[3]) / 2
            
            # Calculate angle between player and mouse
            dx = event.x - player_x
            dy = event.y - player_y
            self.player_direction = math.atan2(dy, dx)
            
    def shoot(self, event):
        if not self.game_over and self.ammo > 0:
            self.ammo -= 1
            player_pos = self.canvas.coords(self.player)
            start_x = (player_pos[0] + player_pos[2]) / 2
            start_y = (player_pos[1] + player_pos[3]) / 2
            
            bullet = {
                'id': self.canvas.create_oval(start_x-2, start_y-2, start_x+2, start_y+2, 
                                           fill='yellow'),
                'dx': math.cos(self.player_direction) * 10,
                'dy': math.sin(self.player_direction) * 10
            }
            self.bullets.append(bullet)
            self.update_status()
            
    def reload(self, event):
        if not self.game_over:
            self.ammo = 30
            self.update_status()
            
    def spawn_enemies(self):
        if len(self.enemies) < 5 and not self.game_over:
            x = random.choice([0, 1000])
            y = random.randint(0, 800)
            enemy = {
                'id': self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='red'),
                'health': 100
            }
            self.enemies.append(enemy)
            
    def spawn_items(self):
        if random.random() < 0.02 and not self.game_over:
            x = random.randint(50, 950)
            y = random.randint(50, 750)
            item_type = random.choice(['health', 'ammo'])
            color = 'green' if item_type == 'health' else 'yellow'
            item = {
                'id': self.canvas.create_rectangle(x, y, x+20, y+20, fill=color),
                'type': item_type
            }
            self.items.append(item)
            
    def move_enemies(self):
        for enemy in self.enemies:
            player_pos = self.canvas.coords(self.player)
            enemy_pos = self.canvas.coords(enemy['id'])
            
            # Calculate direction to player
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                dx = dx/distance * 2
                dy = dy/distance * 2
                self.canvas.move(enemy['id'], dx, dy)
                
            # Check collision with player
            if self.check_collision(player_pos, enemy_pos):
                self.player_health -= 1
                self.update_status()
                
                if self.player_health <= 0:
                    self.game_over = True
                    self.show_game_over()
                    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            self.canvas.move(bullet['id'], bullet['dx'], bullet['dy'])
            bullet_pos = self.canvas.coords(bullet['id'])
            
            # Check collision with enemies
            for enemy in self.enemies[:]:
                enemy_pos = self.canvas.coords(enemy['id'])
                if self.check_collision(bullet_pos, enemy_pos):
                    enemy['health'] -= 34
                    self.canvas.delete(bullet['id'])
                    self.bullets.remove(bullet)
                    
                    if enemy['health'] <= 0:
                        self.canvas.delete(enemy['id'])
                        self.enemies.remove(enemy)
                        self.score += 10
                        self.update_status()
                    break
                    
            # Remove bullets that are off screen
            if (bullet_pos[0] < 0 or bullet_pos[0] > 1000 or
                bullet_pos[1] < 0 or bullet_pos[1] > 800):
                self.canvas.delete(bullet['id'])
                self.bullets.remove(bullet)
                
    def check_items(self):
        player_pos = self.canvas.coords(self.player)
        for item in self.items[:]:
            item_pos = self.canvas.coords(item['id'])
            if self.check_collision(player_pos, item_pos):
                if item['type'] == 'health':
                    self.player_health = min(100, self.player_health + 25)
                else:
                    self.ammo += 30
                    
                self.canvas.delete(item['id'])
                self.items.remove(item)
                self.update_status()
                
    def check_collision(self, pos1, pos2):
        return (pos1[2] >= pos2[0] and pos1[0] <= pos2[2] and
                pos1[3] >= pos2[1] and pos1[1] <= pos2[3])
                
    def update_status(self):
        self.canvas.itemconfig(
            self.status_text,
            text=f"Health: {self.player_health} | Ammo: {self.ammo} | Score: {self.score}"
        )
        
    def show_game_over(self):
        self.canvas.create_text(
            500, 400,
            text=f"Game Over!\nFinal Score: {self.score}\nPress R to restart",
            fill='white',
            font=('Arial', 24),
            justify='center'
        )
        self.root.bind('r', self.restart_game)
        
    def restart_game(self, event=None):
        if self.game_over:
            # Clear canvas
            self.canvas.delete('all')
            
            # Reset variables
            self.player_health = 100
            self.ammo = 30
            self.score = 0
            self.game_over = False
            
            # Clear lists
            self.enemies.clear()
            self.bullets.clear()
            self.items.clear()
            
            # Recreate game elements
            self.player = self.canvas.create_oval(480, 380, 520, 420, fill='blue')
            self.create_obstacles()
            self.status_text = self.canvas.create_text(
                100, 30,
                text=f"Health: {self.player_health} | Ammo: {self.ammo} | Score: {self.score}",
                fill='white',
                font=('Arial', 14)
            )
            
    def update_game(self):
        if not self.game_over:
            self.move_enemies()
            self.update_bullets()
            self.check_items()
            
            if random.random() < 0.02:
                self.spawn_enemies()
            if random.random() < 0.01:
                self.spawn_items()
                
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = PUBGGame()
    game.run()

"""
To play the game:

1. Save as pubg_game.py
2. Run the file
3. Controls:
   - Arrow keys: Move player
   - Mouse: Aim
   - Space: Shoot
   - R: Reload/Restart
   """
   