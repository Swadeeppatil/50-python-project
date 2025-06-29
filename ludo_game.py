import tkinter as tk
from tkinter import messagebox
import random

class LudoGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ludo Game")
        self.root.geometry("800x800")
        
        # Game variables
        self.current_player = 0
        self.players = ['Red', 'Green', 'Yellow', 'Blue']
        self.player_colors = ['red', 'green', 'yellow', 'blue']
        self.dice_value = 0
        self.pieces = {}
        self.home_positions = {}
        self.paths = {}
        
        # Create game board
        self.canvas = tk.Canvas(self.root, width=800, height=700, bg='white')
        self.canvas.pack(pady=20)
        
        # Create board elements
        self.create_board()
        self.create_pieces()
        self.create_controls()
        
        # Initialize game
        self.setup_game()
        
    def create_board(self):
        # Create main board squares
        square_size = 40
        start_x = 200
        start_y = 100
        
        # Create colored home areas
        homes = {
            'Red': (start_x, start_y),
            'Green': (start_x + 6*square_size, start_y),
            'Yellow': (start_x, start_y + 6*square_size),
            'Blue': (start_x + 6*square_size, start_y + 6*square_size)
        }
        
        for color, (x, y) in homes.items():
            self.canvas.create_rectangle(x, y, x + 2*square_size, y + 2*square_size, 
                                      fill=color.lower())
            self.home_positions[color] = (x + square_size, y + square_size)
        
        # Create path
        for i in range(15):
            for j in range(15):
                x = start_x + j * square_size
                y = start_y + i * square_size
                self.canvas.create_rectangle(x, y, x + square_size, y + square_size, 
                                          outline='black')
                
    def create_pieces(self):
        # Create 4 pieces for each player
        for player in self.players:
            self.pieces[player] = []
            x, y = self.home_positions[player]
            for i in range(4):
                piece = self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                             fill=player.lower(), tags=player)
                self.pieces[player].append({
                    'id': piece,
                    'position': 'home',
                    'steps': 0
                })
                x += 40
                
    def create_controls(self):
        # Create dice button
        self.dice_button = tk.Button(self.root, text="Roll Dice", command=self.roll_dice)
        self.dice_button.pack(pady=10)
        
        # Create turn label
        self.turn_label = tk.Label(self.root, 
                                 text=f"Current Turn: {self.players[self.current_player]}", 
                                 font=('Arial', 16))
        self.turn_label.pack()
        
    def setup_game(self):
        # Set up click handlers for pieces
        for player in self.players:
            self.canvas.tag_bind(player, '<Button-1>', self.move_piece)
            
    def roll_dice(self):
        if not self.dice_value:  # Only roll if no move is pending
            self.dice_value = random.randint(1, 6)
            messagebox.showinfo("Dice Roll", f"You rolled a {self.dice_value}!")
            
            # Check if player has any valid moves
            has_valid_move = False
            for piece in self.pieces[self.players[self.current_player]]:
                if self.is_valid_move(piece):
                    has_valid_move = True
                    break
                    
            if not has_valid_move:
                self.next_turn()
                
    def is_valid_move(self, piece):
        if piece['position'] == 'home' and self.dice_value == 6:
            return True
        elif piece['position'] != 'home':
            return True
        return False
        
    def move_piece(self, event):
        if not self.dice_value:
            return
            
        current_color = self.players[self.current_player]
        piece_id = self.canvas.find_closest(event.x, event.y)[0]
        
        # Find the clicked piece
        for piece in self.pieces[current_color]:
            if piece['id'] == piece_id:
                if self.is_valid_move(piece):
                    if piece['position'] == 'home' and self.dice_value == 6:
                        # Move piece out of home
                        self.move_to_start(piece)
                    else:
                        # Move piece along path
                        self.move_along_path(piece)
                    self.next_turn()
                break
                
    def move_to_start(self, piece):
        start_positions = {
            'Red': (280, 100),
            'Green': (440, 180),
            'Yellow': (200, 440),
            'Blue': (520, 520)
        }
        
        color = self.players[self.current_player]
        x, y = start_positions[color]
        self.canvas.coords(piece['id'], x-15, y-15, x+15, y+15)
        piece['position'] = 'board'
        piece['steps'] = 0
        
    def move_along_path(self, piece):
        # Simple movement - just move forward
        current_pos = self.canvas.coords(piece['id'])
        piece['steps'] += self.dice_value
        
        # Move piece based on current position and dice value
        if piece['steps'] <= 50:  # Maximum steps before reaching home
            self.canvas.move(piece['id'], 40 * self.dice_value, 0)
            
        # Check if piece reached home
        if piece['steps'] >= 50:
            self.canvas.delete(piece['id'])
            piece['position'] = 'finished'
            
            # Check if all pieces are home
            all_finished = all(p['position'] == 'finished' 
                             for p in self.pieces[self.players[self.current_player]])
            if all_finished:
                messagebox.showinfo("Winner!", 
                                  f"{self.players[self.current_player]} wins!")
                self.root.quit()
                
    def next_turn(self):
        self.dice_value = 0
        self.current_player = (self.current_player + 1) % 4
        self.turn_label.config(text=f"Current Turn: {self.players[self.current_player]}")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = LudoGame()
    game.run()

"""
- Save as ludo_game.py
- Run the file
- Game Controls:
- Click "Roll Dice" button to roll
- Click on your piece to move it
- Six is required to move piece out of home
- First player to get all pieces to finish wins
"""
