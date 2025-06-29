import tkinter as tk
from tkinter import messagebox
import random

class ConstructionGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Construction Game")
        self.root.geometry("800x600")
        
        # Game variables
        self.money = 1000
        self.materials = {'wood': 50, 'brick': 30, 'steel': 20}
        self.buildings = []
        self.workers = 2
        self.game_time = 0
        self.paused = False
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg='lightblue')
        self.canvas.pack(pady=10)
        
        # Create ground
        self.canvas.create_rectangle(0, 400, 800, 500, fill='brown')
        
        # Create control panel
        self.create_controls()
        
        # Start game loop
        self.update_game()
        
    def create_controls(self):
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill='x', padx=10)
        
        # Status labels
        self.status_label = tk.Label(control_frame, 
            text=f"Money: ${self.money} | Workers: {self.workers}", font=('Arial', 12))
        self.status_label.pack(side='left', padx=5)
        
        self.materials_label = tk.Label(control_frame, 
            text=self.get_materials_text(), font=('Arial', 12))
        self.materials_label.pack(side='left', padx=5)
        
        # Building buttons
        tk.Button(control_frame, text="Build House", 
                 command=lambda: self.start_construction('house')).pack(side='right', padx=5)
        tk.Button(control_frame, text="Build Office", 
                 command=lambda: self.start_construction('office')).pack(side='right', padx=5)
        tk.Button(control_frame, text="Build Factory", 
                 command=lambda: self.start_construction('factory')).pack(side='right', padx=5)
        
        # Resource buttons
        tk.Button(control_frame, text="Buy Materials", 
                 command=self.buy_materials).pack(side='right', padx=5)
        tk.Button(control_frame, text="Hire Worker", 
                 command=self.hire_worker).pack(side='right', padx=5)
        
    def get_materials_text(self):
        return f"Wood: {self.materials['wood']} | Brick: {self.materials['brick']} | Steel: {self.materials['steel']}"
        
    def start_construction(self, building_type):
        costs = {
            'house': {'money': 200, 'wood': 20, 'brick': 10, 'steel': 5},
            'office': {'money': 500, 'wood': 30, 'brick': 25, 'steel': 15},
            'factory': {'money': 1000, 'wood': 50, 'brick': 40, 'steel': 30}
        }
        
        cost = costs[building_type]
        
        # Check resources
        if (self.money >= cost['money'] and 
            all(self.materials[mat] >= cost[mat] for mat in ['wood', 'brick', 'steel'])):
            
            # Deduct resources
            self.money -= cost['money']
            for material in ['wood', 'brick', 'steel']:
                self.materials[material] -= cost[material]
                
            # Start construction
            x = len(self.buildings) * 150 + 50
            if x < 700:  # Check if there's space
                building = {
                    'type': building_type,
                    'progress': 0,
                    'x': x,
                    'id': None
                }
                self.buildings.append(building)
                self.draw_building(building)
                self.update_labels()
            else:
                messagebox.showwarning("No Space", "No more space for new buildings!")
        else:
            messagebox.showwarning("Insufficient Resources", 
                                 "Not enough resources for construction!")
            
    def draw_building(self, building):
        colors = {'house': 'red', 'office': 'blue', 'factory': 'purple'}
        heights = {'house': 100, 'office': 150, 'factory': 200}
        
        height = heights[building['type']]
        y = 400 - height  # Ground level is at y=400
        
        if building['id']:
            self.canvas.delete(building['id'])
            
        # Draw building with progress
        progress_height = height * (building['progress'] / 100)
        building['id'] = self.canvas.create_rectangle(
            building['x'], 400 - progress_height,
            building['x'] + 100, 400,
            fill=colors[building['type']]
        )
        
    def buy_materials(self):
        if self.money >= 100:
            self.money -= 100
            self.materials['wood'] += 20
            self.materials['brick'] += 15
            self.materials['steel'] += 10
            self.update_labels()
        else:
            messagebox.showwarning("Insufficient Funds", "Not enough money!")
            
    def hire_worker(self):
        if self.money >= 200:
            self.money -= 200
            self.workers += 1
            self.update_labels()
        else:
            messagebox.showwarning("Insufficient Funds", "Not enough money!")
            
    def update_labels(self):
        self.status_label.config(text=f"Money: ${self.money} | Workers: {self.workers}")
        self.materials_label.config(text=self.get_materials_text())
        
    def update_construction(self):
        workers_available = self.workers
        
        for building in self.buildings:
            if building['progress'] < 100 and workers_available > 0:
                building['progress'] = min(100, building['progress'] + 1)
                workers_available -= 1
                self.draw_building(building)
                
                # Generate income when building is complete
                if building['progress'] == 100:
                    income = {'house': 50, 'office': 100, 'factory': 200}
                    self.money += income[building['type']]
                    self.update_labels()
                    
    def update_game(self):
        if not self.paused:
            self.game_time += 1
            
            # Update construction progress
            if self.game_time % 10 == 0:  # Update every 10 ticks
                self.update_construction()
                
            # Generate passive income from completed buildings
            if self.game_time % 100 == 0:  # Generate income every 100 ticks
                for building in self.buildings:
                    if building['progress'] == 100:
                        income = {'house': 10, 'office': 25, 'factory': 50}
                        self.money += income[building['type']]
                        self.update_labels()
                        
        self.root.after(100, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = ConstructionGame()
    game.run()