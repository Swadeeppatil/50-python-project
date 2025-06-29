import tkinter as tk
from tkinter import messagebox
import random
import math

class GTAGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GTA Style Game")
        self.root.geometry("1000x800")
        
        # Game canvas
        self.canvas = tk.Canvas(self.root, width=1000, height=800, bg='darkgray')
        self.canvas.pack()
        
        # Game variables
        self.player_x = 500
        self.player_y = 400
        self.player_speed = 5
        self.player_health = 100
        self.money = 0
        self.score = 0
        self.game_over = False
        self.current_weapon = "fist"
        
        # Create game elements
        self.create_city()
        self.create_player()
        self.create_npcs()
        self.create_vehicles()
        
        # Key bindings
        self.setup_controls()
        
        # Start game loop
        self.update_game()
        
    def create_city(self):
        # Create buildings
        for _ in range(20):
            x = random.randint(0, 900)
            y = random.randint(0, 700)
            width = random.randint(50, 150)
            height = random.randint(100, 200)
            self.canvas.create_rectangle(x, y, x+width, y+height, fill='gray')
            
        # Create roads
        for i in range(0, 1000, 200):
            self.canvas.create_line(i, 0, i, 800, fill='yellow', width=2)
            self.canvas.create_line(0, i, 1000, i, fill='yellow', width=2)
            
    def create_player(self):
        self.player = self.canvas.create_oval(
            self.player_x-15, self.player_y-15,
            self.player_x+15, self.player_y+15,
            fill='blue', tags='player'
        )
        
    def create_npcs(self):
        self.npcs = []
        for _ in range(10):
            x = random.randint(0, 1000)
            y = random.randint(0, 800)
            npc = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='green')
            self.npcs.append({'id': npc, 'x': x, 'y': y, 'dx': 1, 'dy': 1})
            
    def create_vehicles(self):
        self.vehicles = []
        colors = ['red', 'yellow', 'orange', 'purple']
        for _ in range(5):
            x = random.randint(0, 900)
            y = random.randint(0, 700)
            color = random.choice(colors)
            vehicle = self.canvas.create_rectangle(x, y, x+40, y+20, fill=color)
            self.vehicles.append({
                'id': vehicle,
                'x': x,
                'y': y,
                'speed': random.randint(2, 5),
                'direction': random.choice(['h', 'v'])
            })
            
    def setup_controls(self):
        self.root.bind('<Left>', lambda e: self.move_player(-1, 0))
        self.root.bind('<Right>', lambda e: self.move_player(1, 0))
        self.root.bind('<Up>', lambda e: self.move_player(0, -1))
        self.root.bind('<Down>', lambda e: self.move_player(0, 1))
        self.root.bind('<space>', self.attack)
        self.root.bind('v', self.steal_vehicle)
        self.root.bind('r', self.restart_game)
        
    def move_player(self, dx, dy):
        if not self.game_over:
            new_x = self.player_x + dx * self.player_speed
            new_y = self.player_y + dy * self.player_speed
            
            if 0 <= new_x <= 1000 and 0 <= new_y <= 800:
                self.player_x = new_x
                self.player_y = new_y
                self.canvas.coords(
                    self.player,
                    new_x-15, new_y-15,
                    new_x+15, new_y+15
                )
                
    def attack(self, event):
        if not self.game_over:
            # Check for nearby NPCs
            for npc in self.npcs[:]:
                npc_coords = self.canvas.coords(npc['id'])
                distance = math.sqrt(
                    (self.player_x - (npc_coords[0] + 10))**2 +
                    (self.player_y - (npc_coords[1] + 10))**2
                )
                
                if distance < 50:  # Attack range
                    self.canvas.delete(npc['id'])
                    self.npcs.remove(npc)
                    self.money += 50
                    self.score += 100
                    
    def steal_vehicle(self, event):
        if not self.game_over:
            for vehicle in self.vehicles:
                vehicle_coords = self.canvas.coords(vehicle['id'])
                distance = math.sqrt(
                    (self.player_x - (vehicle_coords[0] + 20))**2 +
                    (self.player_y - (vehicle_coords[1] + 10))**2
                )
                
                if distance < 30:  # Stealing range
                    self.player_speed = 10  # Faster in vehicle
                    self.canvas.itemconfig(self.player, fill='red')
                    return
                    
    def update_npcs(self):
        for npc in self.npcs:
            # Random movement
            if random.random() < 0.02:
                npc['dx'] = random.choice([-1, 0, 1])
                npc['dy'] = random.choice([-1, 0, 1])
                
            new_x = npc['x'] + npc['dx']
            new_y = npc['y'] + npc['dy']
            
            if 0 <= new_x <= 1000 and 0 <= new_y <= 800:
                npc['x'] = new_x
                npc['y'] = new_y
                self.canvas.coords(
                    npc['id'],
                    new_x-10, new_y-10,
                    new_x+10, new_y+10
                )
                
    def update_vehicles(self):
        for vehicle in self.vehicles:
            if vehicle['direction'] == 'h':
                vehicle['x'] += vehicle['speed']
                if vehicle['x'] > 1000:
                    vehicle['x'] = 0
            else:
                vehicle['y'] += vehicle['speed']
                if vehicle['y'] > 800:
                    vehicle['y'] = 0
                    
            self.canvas.coords(
                vehicle['id'],
                vehicle['x'], vehicle['y'],
                vehicle['x']+40, vehicle['y']+20
            )
            
    def check_police(self):
        if self.score > 500 and random.random() < 0.01:
            # Spawn police
            x = random.randint(0, 1000)
            y = random.randint(0, 800)
            police = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='blue')
            self.npcs.append({'id': police, 'x': x, 'y': y, 'dx': 1, 'dy': 1})
            
    def update_game(self):
        if not self.game_over:
            self.update_npcs()
            self.update_vehicles()
            self.check_police()
            
            # Update status
            self.canvas.delete('status')
            self.canvas.create_text(
                100, 30,
                text=f"Health: {self.player_health}\nMoney: ${self.money}\nScore: {self.score}",
                fill='white',
                tags='status'
            )
            
            # Check game over conditions
            if self.player_health <= 0:
                self.game_over = True
                self.show_game_over()
                
        self.root.after(50, self.update_game)
        
    def show_game_over(self):
        self.canvas.create_text(
            500, 400,
            text=f"Game Over!\nFinal Score: {self.score}\nPress R to restart",
            font=('Arial', 24),
            fill='red'
        )
        
    def restart_game(self, event=None):
        if self.game_over:
            self.canvas.delete('all')
            self.__init__()
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = GTAGame()
    game.run()

"""
To play the game:

1. Save as gta_game.py
2. Run the file
3. Controls:
   - Arrow keys: Move player
   - Space: Attack/Fight
   - V: Steal vehicle
   - R: Restart game
Features:

- City environment with buildings and roads
- Player movement and combat
- NPCs with random movement
- Vehicles to steal
- Money and scoring system
- Police spawning at higher scores
- Health system
- Game over conditions
- Vehicle theft mechanics
The goal is to survive, steal vehicles, and earn money while avoiding police! Try to get the highest score possible.
"""