import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import random
import json
import os
from PIL import Image, ImageTk

class FarmingGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Farming Simulator")
        self.window.geometry("1200x800")
        self.window.resizable(False, False)
        
        # Game variables
        self.money = 10000
        self.crops = {}
        self.vehicles = {
            'tractor': {'owned': True, 'speed': 5, 'x': 100, 'y': 100},
            'truck': {'owned': False, 'speed': 7, 'price': 5000, 'x': 200, 'y': 100},
            'harvester': {'owned': False, 'speed': 4, 'price': 7000, 'x': 300, 'y': 100}
        }
        self.selected_vehicle = 'tractor'
        self.selected_crop = None
        
        # Load images
        self.load_images()
        self.create_gui()
        
        # Game loop
        self.update_game()
        
    def load_images(self):
        self.images = {
            'tractor': ImageTk.PhotoImage(Image.open("assets/tractor.png").resize((50, 50))),
            'truck': ImageTk.PhotoImage(Image.open("assets/truck.png").resize((50, 50))),
            'harvester': ImageTk.PhotoImage(Image.open("assets/harvester.png").resize((50, 50))),
            'soil': ImageTk.PhotoImage(Image.open("assets/soil.png").resize((40, 40))),
            'tree': ImageTk.PhotoImage(Image.open("assets/tree.png").resize((40, 40))),
            'wheat': ImageTk.PhotoImage(Image.open("assets/wheat.png").resize((40, 40))),
            'corn': ImageTk.PhotoImage(Image.open("assets/corn.png").resize((40, 40)))
        }
        
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Game controls
        left_panel = ttk.LabelFrame(main_frame, text="Controls")
        left_panel.pack(side='left', fill='y', padx=5)
        
        # Vehicle selection
        vehicle_frame = ttk.LabelFrame(left_panel, text="Vehicles")
        vehicle_frame.pack(fill='x', pady=5)
        
        for vehicle in self.vehicles:
            btn = ttk.Button(vehicle_frame, text=vehicle.title(),
                           command=lambda v=vehicle: self.select_vehicle(v))
            btn.pack(fill='x', pady=2)
        
        # Crop selection
        crop_frame = ttk.LabelFrame(left_panel, text="Crops")
        crop_frame.pack(fill='x', pady=5)
        
        crops = ['tree', 'wheat', 'corn']
        for crop in crops:
            btn = ttk.Button(crop_frame, text=crop.title(),
                           command=lambda c=crop: self.select_crop(c))
            btn.pack(fill='x', pady=2)
        
        # Status display
        status_frame = ttk.LabelFrame(left_panel, text="Status")
        status_frame.pack(fill='x', pady=5)
        
        self.money_label = ttk.Label(status_frame, text=f"Money: ${self.money}")
        self.money_label.pack(fill='x')
        
        # Game canvas
        self.canvas = tk.Canvas(main_frame, width=800, height=600, bg='#90EE90')
        self.canvas.pack(side='left', padx=5)
        
        # Canvas bindings
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<KeyPress>", self.key_press)
        self.canvas.focus_set()
        
        # Market panel
        market_panel = ttk.LabelFrame(main_frame, text="Market")
        market_panel.pack(side='right', fill='y', padx=5)
        
        # Market prices
        self.market_prices = {
            'tree': random.randint(100, 500),
            'wheat': random.randint(50, 200),
            'corn': random.randint(75, 300)
        }
        
        for crop, price in self.market_prices.items():
            ttk.Label(market_panel,
                     text=f"{crop.title()}: ${price}").pack(fill='x', pady=2)
        
        ttk.Button(market_panel, text="Sell Crops",
                  command=self.sell_crops).pack(fill='x', pady=10)
        
    def select_vehicle(self, vehicle):
        if not self.vehicles[vehicle]['owned']:
            if self.money >= self.vehicles[vehicle]['price']:
                if messagebox.askyesno("Purchase Vehicle",
                                     f"Buy {vehicle} for ${self.vehicles[vehicle]['price']}?"):
                    self.money -= self.vehicles[vehicle]['price']
                    self.vehicles[vehicle]['owned'] = True
                    self.update_money_display()
            else:
                messagebox.showwarning("Insufficient Funds",
                                     "Not enough money to buy this vehicle!")
            return
            
        self.selected_vehicle = vehicle
        
    def select_crop(self, crop):
        self.selected_crop = crop
        
    def canvas_click(self, event):
        if self.selected_crop:
            # Check if space is empty
            overlapping = self.canvas.find_overlapping(
                event.x-20, event.y-20, event.x+20, event.y+20)
            
            if not overlapping:
                # Plant crop
                crop_id = self.canvas.create_image(
                    event.x, event.y, image=self.images[self.selected_crop])
                self.crops[crop_id] = {
                    'type': self.selected_crop,
                    'growth': 0,
                    'ready': False
                }
                
    def key_press(self, event):
        vehicle = self.vehicles[self.selected_vehicle]
        speed = vehicle['speed']
        
        if event.keysym == 'Up':
            vehicle['y'] -= speed
        elif event.keysym == 'Down':
            vehicle['y'] += speed
        elif event.keysym == 'Left':
            vehicle['x'] -= speed
        elif event.keysym == 'Right':
            vehicle['x'] += speed
            
        self.update_game()
        
    def update_game(self):
        self.canvas.delete('vehicle')
        
        # Draw vehicles
        for vehicle_type, vehicle in self.vehicles.items():
            if vehicle['owned']:
                self.canvas.create_image(
                    vehicle['x'], vehicle['y'],
                    image=self.images[vehicle_type],
                    tags='vehicle')
        
        # Update crops
        for crop_id, crop in list(self.crops.items()):
            if not crop['ready']:
                crop['growth'] += 0.1
                if crop['growth'] >= 100:
                    crop['ready'] = True
                    self.canvas.itemconfig(crop_id,
                                         image=self.images[crop['type']])
        
        # Update market prices periodically
        if random.random() < 0.01:
            for crop in self.market_prices:
                self.market_prices[crop] = random.randint(50, 500)
        
        self.window.after(100, self.update_game)
        
    def sell_crops(self):
        total = 0
        for crop_id, crop in list(self.crops.items()):
            if crop['ready']:
                price = self.market_prices[crop['type']]
                total += price
                self.canvas.delete(crop_id)
                del self.crops[crop_id]
        
        if total > 0:
            self.money += total
            self.update_money_display()
            messagebox.showinfo("Sale Complete",
                              f"Sold crops for ${total}")
        else:
            messagebox.showinfo("No Sale",
                              "No ready crops to sell!")
            
    def update_money_display(self):
        self.money_label.config(text=f"Money: ${self.money}")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = FarmingGame()
    game.run()