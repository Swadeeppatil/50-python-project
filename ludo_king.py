import tkinter as tk
from tkinter import ttk, messagebox
import random
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class LudoBoard:
    def __init__(self, master):
        self.master = master
        self.cell_size = 50
        self.board_size = 15
        self.canvas = tk.Canvas(master, width=self.cell_size * self.board_size,
                              height=self.cell_size * self.board_size)
        self.canvas.pack(padx=20, pady=20)
        self.create_board()
        
    def create_board(self):
        # Draw base board
        colors = {
            'Red': '#FF4444',
            'Green': '#44FF44',
            'Yellow': '#FFFF44',
            'Blue': '#4444FF'
        }
        
        # Draw home areas
        home_positions = {
            'Red': (0, 0),
            'Green': (0, 9),
            'Yellow': (9, 9),
            'Blue': (9, 0)
        }
        
        for color, pos in home_positions.items():
            self.draw_home(pos[0], pos[1], colors[color])
            
        # Draw paths
        self.draw_paths()
        
        # Draw center
        self.canvas.create_rectangle(
            self.cell_size * 6, self.cell_size * 6,
            self.cell_size * 9, self.cell_size * 9,
            fill='#FFFFFF', outline='black'
        )
        
    def draw_home(self, start_x, start_y, color):
        # Draw 6x6 home area
        self.canvas.create_rectangle(
            start_x * self.cell_size, start_y * self.cell_size,
            (start_x + 6) * self.cell_size, (start_y + 6) * self.cell_size,
            fill=color, outline='black'
        )
        
        # Draw starting circles
        circle_positions = [(1, 1), (1, 4), (4, 1), (4, 4)]
        for cx, cy in circle_positions:
            self.canvas.create_oval(
                (start_x + cx) * self.cell_size,
                (start_y + cy) * self.cell_size,
                (start_x + cx + 1) * self.cell_size,
                (start_y + cy + 1) * self.cell_size,
                fill='white', outline='black'
            )
            
    def draw_paths(self):
        # Draw vertical paths
        for i in range(6):
            self.canvas.create_rectangle(
                7 * self.cell_size, i * self.cell_size,
                8 * self.cell_size, (i + 1) * self.cell_size,
                fill='#DDDDDD', outline='black'
            )
            self.canvas.create_rectangle(
                7 * self.cell_size, (i + 9) * self.cell_size,
                8 * self.cell_size, (i + 10) * self.cell_size,
                fill='#DDDDDD', outline='black'
            )
            
        # Draw horizontal paths
        for i in range(6):
            self.canvas.create_rectangle(
                i * self.cell_size, 7 * self.cell_size,
                (i + 1) * self.cell_size, 8 * self.cell_size,
                fill='#DDDDDD', outline='black'
            )
            self.canvas.create_rectangle(
                (i + 9) * self.cell_size, 7 * self.cell_size,
                (i + 10) * self.cell_size, 8 * self.cell_size,
                fill='#DDDDDD', outline='black'
            )

class LudoGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ludo King")
        self.window.geometry("1000x800")
        self.window.configure(bg='#F0F0F0')
        
        self.players = ['Red', 'Green', 'Yellow', 'Blue']
        self.current_player = 0
        self.pawns = {color: [None] * 4 for color in self.players}
        self.dice_value = 0
        self.game_active = False
        
        self.create_gui()
        self.setup_game()
        
    def create_gui(self):
        # Create main board
        self.board = LudoBoard(self.window)
        
        # Control panel
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Player info
        self.player_label = ttk.Label(control_frame,
                                    text=f"Current Player: {self.players[self.current_player]}")
        self.player_label.pack(side='left', padx=10)
        
        # Dice frame
        dice_frame = ttk.Frame(control_frame)
        dice_frame.pack(side='left', padx=20)
        
        self.dice_button = ttk.Button(dice_frame, text="Roll Dice",
                                    command=self.roll_dice)
        self.dice_button.pack(side='left')
        
        self.dice_label = ttk.Label(dice_frame, text="Dice: 0")
        self.dice_label.pack(side='left', padx=10)
        
        # Game controls
        ttk.Button(control_frame, text="New Game",
                  command=self.new_game).pack(side='right', padx=10)
        
        # Status bar
        self.status_bar = ttk.Label(self.window, text="Welcome to Ludo King!")
        self.status_bar.pack(side='bottom', fill='x', padx=10, pady=5)
        
    def setup_game(self):
        self.game_active = True
        self.current_player = 0
        self.dice_value = 0
        self.update_status("Game started! Red player's turn.")
        
    def roll_dice(self):
        if not self.game_active:
            return
            
        self.dice_value = random.randint(1, 6)
        self.dice_label.config(text=f"Dice: {self.dice_value}")
        
        if self.dice_value == 6:
            self.update_status(f"{self.players[self.current_player]} got 6! Play again!")
        else:
            self.next_turn()
            
    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.player_label.config(text=f"Current Player: {self.players[self.current_player]}")
        self.update_status(f"{self.players[self.current_player]}'s turn")
        
    def new_game(self):
        if messagebox.askyesno("New Game", "Start a new game?"):
            self.setup_game()
            self.update_status("New game started! Red player's turn.")
            
    def update_status(self, message):
        self.status_bar.config(text=message)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    try:
        game = LudoGame()
        game.run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")