import tkinter as tk
from tkinter import messagebox

class ChessGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Game")
        self.root.geometry("600x600")
        
        # Game variables
        self.selected_piece = None
        self.current_player = 'white'
        self.board = self.initialize_board()
        
        # Create game board
        self.squares = {}
        self.create_board()
        
        # Place pieces
        self.place_pieces()
        
    def initialize_board(self):
        # Initialize piece positions
        board = {
            # Black pieces
            (0,0): 'black_rook', (1,0): 'black_knight', (2,0): 'black_bishop',
            (3,0): 'black_queen', (4,0): 'black_king', (5,0): 'black_bishop',
            (6,0): 'black_knight', (7,0): 'black_rook',
            # Black pawns
            (0,1): 'black_pawn', (1,1): 'black_pawn', (2,1): 'black_pawn',
            (3,1): 'black_pawn', (4,1): 'black_pawn', (5,1): 'black_pawn',
            (6,1): 'black_pawn', (7,1): 'black_pawn',
            # White pieces
            (0,7): 'white_rook', (1,7): 'white_knight', (2,7): 'white_bishop',
            (3,7): 'white_queen', (4,7): 'white_king', (5,7): 'white_bishop',
            (6,7): 'white_knight', (7,7): 'white_rook',
            # White pawns
            (0,6): 'white_pawn', (1,6): 'white_pawn', (2,6): 'white_pawn',
            (3,6): 'white_pawn', (4,6): 'white_pawn', (5,6): 'white_pawn',
            (6,6): 'white_pawn', (7,6): 'white_pawn'
        }
        return board
        
    def create_board(self):
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                square = tk.Button(self.root, bg=color, width=5, height=2,
                                 command=lambda r=row, c=col: self.square_clicked(r, c))
                square.grid(row=row, column=col)
                self.squares[(col, row)] = square
                
    def place_pieces(self):
        piece_symbols = {
            'white_king': '♔', 'white_queen': '♕', 'white_rook': '♖',
            'white_bishop': '♗', 'white_knight': '♘', 'white_pawn': '♙',
            'black_king': '♚', 'black_queen': '♛', 'black_rook': '♜',
            'black_bishop': '♝', 'black_knight': '♞', 'black_pawn': '♟'
        }
        
        for pos, piece in self.board.items():
            self.squares[pos].config(text=piece_symbols[piece], font=('Arial', 20))
            
    def square_clicked(self, row, col):
        position = (col, row)
        
        # If no piece is selected and clicked square has a piece
        if not self.selected_piece and position in self.board:
            piece = self.board[position]
            if piece.startswith(self.current_player):
                self.selected_piece = position
                self.squares[position].config(bg='yellow')
                
        # If a piece is selected
        elif self.selected_piece:
            if self.is_valid_move(self.selected_piece, position):
                self.move_piece(self.selected_piece, position)
                self.switch_player()
            
            # Reset selection
            old_pos = self.selected_piece
            self.selected_piece = None
            self.update_square_color(old_pos)
            
    def is_valid_move(self, start, end):
        piece = self.board[start]
        
        # Basic validation: can't capture own pieces
        if end in self.board and self.board[end].startswith(self.current_player):
            return False
            
        # Implement piece-specific movement rules
        piece_type = piece.split('_')[1]
        start_x, start_y = start
        end_x, end_y = end
        
        if piece_type == 'pawn':
            direction = -1 if self.current_player == 'white' else 1
            if start_x == end_x:  # Moving forward
                if end_y == start_y + direction:
                    return end not in self.board
                if (start_y == 6 and self.current_player == 'white') or \
                   (start_y == 1 and self.current_player == 'black'):
                    if end_y == start_y + 2 * direction:
                        return end not in self.board
            elif abs(start_x - end_x) == 1 and end_y == start_y + direction:
                return end in self.board  # Capture diagonally
            return False
            
        elif piece_type == 'rook':
            return start_x == end_x or start_y == end_y
            
        elif piece_type == 'knight':
            dx = abs(end_x - start_x)
            dy = abs(end_y - start_y)
            return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
            
        elif piece_type == 'bishop':
            return abs(end_x - start_x) == abs(end_y - start_y)
            
        elif piece_type == 'queen':
            return (start_x == end_x or start_y == end_y or 
                   abs(end_x - start_x) == abs(end_y - start_y))
            
        elif piece_type == 'king':
            return abs(end_x - start_x) <= 1 and abs(end_y - start_y) <= 1
            
        return True
        
    def move_piece(self, start, end):
        # Update board state
        piece = self.board[start]
        self.board[end] = piece
        del self.board[start]
        
        # Update GUI
        self.squares[end].config(text=self.squares[start].cget('text'))
        self.squares[start].config(text='')
        
        # Check for win condition (king capture)
        if end in self.board and 'king' in self.board[end]:
            self.game_over()
            
    def switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
    def update_square_color(self, position):
        row = position[1]
        col = position[0]
        color = 'white' if (row + col) % 2 == 0 else 'gray'
        self.squares[position].config(bg=color)
        
    def game_over(self):
        winner = 'White' if self.current_player == 'white' else 'Black'
        messagebox.showinfo("Game Over", f"{winner} wins!")
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run()

"""
## Trae AI
Used 1 Reference

Here's a complete Basketball Game using Python Tkinter:

```python
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
 ```
```

To play the game:

1. Save as basketball_game.py
2. Run the file
3. Controls:
   - Left/Right Arrow: Move player
   - Space (Hold): Charge shot power
   - Space (Release): Shoot ball
Features:

- Basketball court with basket and backboard
- Player movement
- Ball physics
- Power meter for shots
- Score tracking
- Time limit
- Game over screen
- Simple animations
- Collision detection
- Realistic ball trajectory
Try to score as many baskets as possible within the time limit! Hold space to charge your shot power and release to shoot.

## Swadeep Patil
Copy

Delete

create chess game using python tkinter gui . dont write code step by step.write all code at onr time in one file .understand

## Trae AI
Used 1 Reference

Here's a complete Chess Game using Python Tkinter:

```python
import tkinter as tk
from tkinter import messagebox

class ChessGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Game")
        self.root.geometry("600x600")
        
        # Game variables
        self.selected_piece = None
        self.current_player = 'white'
        self.board = self.initialize_board()
        
        # Create game board
        self.squares = {}
        self.create_board()
        
        # Place pieces
        self.place_pieces()
        
    def initialize_board(self):
        # Initialize piece positions
        board = {
            # Black pieces
            (0,0): 'black_rook', (1,0): 'black_knight', (2,0): 'black_bishop',
            (3,0): 'black_queen', (4,0): 'black_king', (5,0): 'black_bishop',
            (6,0): 'black_knight', (7,0): 'black_rook',
            # Black pawns
            (0,1): 'black_pawn', (1,1): 'black_pawn', (2,1): 'black_pawn',
            (3,1): 'black_pawn', (4,1): 'black_pawn', (5,1): 'black_pawn',
            (6,1): 'black_pawn', (7,1): 'black_pawn',
            # White pieces
            (0,7): 'white_rook', (1,7): 'white_knight', (2,7): 'white_bishop',
            (3,7): 'white_queen', (4,7): 'white_king', (5,7): 'white_bishop',
            (6,7): 'white_knight', (7,7): 'white_rook',
            # White pawns
            (0,6): 'white_pawn', (1,6): 'white_pawn', (2,6): 'white_pawn',
            (3,6): 'white_pawn', (4,6): 'white_pawn', (5,6): 'white_pawn',
            (6,6): 'white_pawn', (7,6): 'white_pawn'
        }
        return board
        
    def create_board(self):
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                square = tk.Button(self.root, bg=color, width=5, height=2,
                                 command=lambda r=row, c=col: self.square_clicked(r, c))
                square.grid(row=row, column=col)
                self.squares[(col, row)] = square
                
    def place_pieces(self):
        piece_symbols = {
            'white_king': '♔', 'white_queen': '♕', 'white_rook': '♖',
            'white_bishop': '♗', 'white_knight': '♘', 'white_pawn': '♙',
            'black_king': '♚', 'black_queen': '♛', 'black_rook': '♜',
            'black_bishop': '♝', 'black_knight': '♞', 'black_pawn': '♟'
        }
        
        for pos, piece in self.board.items():
            self.squares[pos].config(text=piece_symbols[piece], font=('Arial', 20))
            
    def square_clicked(self, row, col):
        position = (col, row)
        
        # If no piece is selected and clicked square has a piece
        if not self.selected_piece and position in self.board:
            piece = self.board[position]
            if piece.startswith(self.current_player):
                self.selected_piece = position
                self.squares[position].config(bg='yellow')
                
        # If a piece is selected
        elif self.selected_piece:
            if self.is_valid_move(self.selected_piece, position):
                self.move_piece(self.selected_piece, position)
                self.switch_player()
            
            # Reset selection
            old_pos = self.selected_piece
            self.selected_piece = None
            self.update_square_color(old_pos)
            
    def is_valid_move(self, start, end):
        piece = self.board[start]
        
        # Basic validation: can't capture own pieces
        if end in self.board and self.board[end].startswith(self.current_player):
            return False
            
        # Implement piece-specific movement rules
        piece_type = piece.split('_')[1]
        start_x, start_y = start
        end_x, end_y = end
        
        if piece_type == 'pawn':
            direction = -1 if self.current_player == 'white' else 1
            if start_x == end_x:  # Moving forward
                if end_y == start_y + direction:
                    return end not in self.board
                if (start_y == 6 and self.current_player == 'white') or \
                   (start_y == 1 and self.current_player == 'black'):
                    if end_y == start_y + 2 * direction:
                        return end not in self.board
            elif abs(start_x - end_x) == 1 and end_y == start_y + direction:
                return end in self.board  # Capture diagonally
            return False
            
        elif piece_type == 'rook':
            return start_x == end_x or start_y == end_y
            
        elif piece_type == 'knight':
            dx = abs(end_x - start_x)
            dy = abs(end_y - start_y)
            return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
            
        elif piece_type == 'bishop':
            return abs(end_x - start_x) == abs(end_y - start_y)
            
        elif piece_type == 'queen':
            return (start_x == end_x or start_y == end_y or 
                   abs(end_x - start_x) == abs(end_y - start_y))
            
        elif piece_type == 'king':
            return abs(end_x - start_x) <= 1 and abs(end_y - start_y) <= 1
            
        return True
        
    def move_piece(self, start, end):
        # Update board state
        piece = self.board[start]
        self.board[end] = piece
        del self.board[start]
        
        # Update GUI
        self.squares[end].config(text=self.squares[start].cget('text'))
        self.squares[start].config(text='')
        
        # Check for win condition (king capture)
        if end in self.board and 'king' in self.board[end]:
            self.game_over()
            
    def switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
    def update_square_color(self, position):
        row = position[1]
        col = position[0]
        color = 'white' if (row + col) % 2 == 0 else 'gray'
        self.squares[position].config(bg=color)
        
    def game_over(self):
        winner = 'White' if self.current_player == 'white' else 'Black'
        messagebox.showinfo("Game Over", f"{winner} wins!")
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
 ```
```

To play the game:

1. Save as chess_game.py
2. Run the file
3. Game Rules:
   - Click to select a piece (highlights in yellow)
   - Click destination square to move
   - White moves first
   - Take turns moving pieces
   - Capture the king to win
   """
   