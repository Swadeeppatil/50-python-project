import tkinter as tk
import random

class PuzzleGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sliding Puzzle")
        
        self.moves = 0
        self.tiles = []
        self.empty_pos = (2, 2)
        
        # Create buttons
        for i in range(3):
            row = []
            for j in range(3):
                if i == 2 and j == 2:
                    button = tk.Button(self.root, text="", width=10, height=5)
                else:
                    number = i * 3 + j + 1
                    button = tk.Button(self.root, text=str(number), 
                                     width=10, height=5,
                                     command=lambda x=i, y=j: self.move_tile(x, y))
                button.grid(row=i, column=j, padx=2, pady=2)
                row.append(button)
            self.tiles.append(row)
            
        # Shuffle button
        tk.Button(self.root, text="Shuffle", 
                 command=self.shuffle).grid(row=3, column=0, columnspan=3, pady=10)
        
        # Moves counter
        self.moves_label = tk.Label(self.root, text="Moves: 0")
        self.moves_label.grid(row=4, column=0, columnspan=3)
        
    def move_tile(self, i, j):
        # Check if clicked tile is adjacent to empty space
        if (abs(i - self.empty_pos[0]) == 1 and j == self.empty_pos[1]) or \
           (abs(j - self.empty_pos[1]) == 1 and i == self.empty_pos[0]):
            # Swap tiles
            self.tiles[self.empty_pos[0]][self.empty_pos[1]].config(
                text=self.tiles[i][j].cget("text"))
            self.tiles[i][j].config(text="")
            self.empty_pos = (i, j)
            
            # Update moves counter
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            
            # Check if puzzle is solved
            self.check_win()
            
    def shuffle(self):
        numbers = list(range(1, 9)) + [""]
        random.shuffle(numbers)
        
        for i in range(3):
            for j in range(3):
                number = numbers[i * 3 + j]
                self.tiles[i][j].config(text=str(number))
                if number == "":
                    self.empty_pos = (i, j)
                    
        self.moves = 0
        self.moves_label.config(text="Moves: 0")
        
    def check_win(self):
        correct = list(range(1, 9)) + [""]
        current = []
        
        for i in range(3):
            for j in range(3):
                current.append(self.tiles[i][j].cget("text"))
                
        if current == [str(x) for x in correct]:
            tk.messagebox.showinfo("Congratulations!", 
                                 f"You solved the puzzle in {self.moves} moves!")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = PuzzleGame()
    game.run()