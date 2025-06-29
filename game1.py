import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

class CricketGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cricket Game")
        self.root.geometry("1200x700")
        
        # Game variables
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.target = 0
        self.current_innings = 1
        self.game_over = False
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create game canvas
        self.canvas = tk.Canvas(self.main_frame, width=1200, height=600, bg='green')
        self.canvas.pack(pady=10)
        
        # Create cricket field
        self.create_field()
        
        # Create scoreboard
        self.create_scoreboard()
        
        # Create players
        self.create_players()
        
        # Create control buttons
        self.create_controls()
        
        # Start game
        self.update_game()
        
    def create_field(self):
        # Draw pitch
        self.canvas.create_rectangle(500, 250, 700, 450, fill='brown')
        self.canvas.create_rectangle(550, 250, 650, 450, fill='tan')
        
        # Draw boundary
        self.canvas.create_oval(50, 50, 1150, 550, outline='white', width=2)
        
        # Draw crease
        self.canvas.create_line(575, 250, 625, 250, fill='white', width=2)
        self.canvas.create_line(575, 450, 625, 450, fill='white', width=2)
        
    def create_players(self):
        # Create batsman
        self.batsman = self.canvas.create_oval(580, 420, 600, 440, fill='blue')
        
        # Create bowler
        self.bowler = self.canvas.create_oval(580, 280, 600, 300, fill='red')
        
        # Create fielders
        self.fielders = []
        fielder_positions = [
            (400, 300), (800, 300),
            (500, 150), (700, 150),
            (300, 400), (900, 400)
        ]
        for x, y in fielder_positions:
            fielder = self.canvas.create_oval(x, y, x+20, y+20, fill='yellow')
            self.fielders.append(fielder)
            
    def create_scoreboard(self):
        self.score_var = tk.StringVar(value="Score: 0/0")
        self.overs_var = tk.StringVar(value="Overs: 0.0")
        
        ttk.Label(self.main_frame, textvariable=self.score_var, font=('Arial', 20)).pack(side=tk.LEFT, padx=20)
        ttk.Label(self.main_frame, textvariable=self.overs_var, font=('Arial', 20)).pack(side=tk.RIGHT, padx=20)
        
    def create_controls(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.BOTTOM, pady=10)
        
        shots = ['Straight Drive', 'Cover Drive', 'Pull Shot', 'Defensive']
        for shot in shots:
            ttk.Button(control_frame, text=shot, 
                      command=lambda s=shot: self.play_shot(s)).pack(side=tk.LEFT, padx=5)
            
    def play_shot(self, shot_type):
        if self.game_over:
            return
            
        # Simulate ball movement
        self.animate_delivery()
        
        # Calculate outcome
        outcome = self.calculate_outcome(shot_type)
        
        # Update score
        self.update_score(outcome)
        
    def animate_delivery(self):
        start_x, start_y = self.canvas.coords(self.bowler)[:2]
        end_x, end_y = self.canvas.coords(self.batsman)[:2]
        
        # Create ball
        ball = self.canvas.create_oval(start_x+10, start_y+10, start_x+20, start_y+20, fill='white')
        
        # Animate ball movement
        steps = 10
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        for _ in range(steps):
            self.canvas.move(ball, dx, dy)
            self.canvas.update()
            time.sleep(0.05)
            
        self.canvas.delete(ball)
        
    def calculate_outcome(self, shot_type):
        outcomes = {
            'Straight Drive': [0, 1, 4, 6, 'out'],
            'Cover Drive': [0, 1, 2, 4, 'out'],
            'Pull Shot': [0, 2, 4, 6, 'out'],
            'Defensive': [0, 0, 1, 'out']
        }
        
        return random.choice(outcomes[shot_type])
        
    def update_score(self, outcome):
        if outcome == 'out':
            self.wickets += 1
            messagebox.showinfo("Wicket!", "You're out!")
        else:
            self.score += outcome
            
        self.balls += 1
        if self.balls == 6:
            self.balls = 0
            self.overs += 1
            
        self.score_var.set(f"Score: {self.score}/{self.wickets}")
        self.overs_var.set(f"Overs: {self.overs}.{self.balls}")
        
        # Check innings/game end conditions
        if self.wickets == 10 or self.overs == 5:
            self.end_innings()
            
    def end_innings(self):
        if self.current_innings == 1:
            self.target = self.score + 1
            messagebox.showinfo("Innings Over", 
                              f"First innings: {self.score}/{self.wickets}\nTarget: {self.target}")
            self.reset_innings()
        else:
            self.end_game()
            
    def reset_innings(self):
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.current_innings = 2
        self.score_var.set(f"Score: {self.score}/{self.wickets}")
        self.overs_var.set(f"Overs: {self.overs}.{self.balls}")
        
    def end_game(self):
        self.game_over = True
        winner = "Batting Team" if self.score >= self.target else "Bowling Team"
        messagebox.showinfo("Game Over", f"{winner} wins!")
        
        if messagebox.askyesno("Play Again?", "Would you like to play another game?"):
            self.reset_game()
            
    def reset_game(self):
        self.score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.target = 0
        self.current_innings = 1
        self.game_over = False
        self.score_var.set(f"Score: {self.score}/{self.wickets}")
        self.overs_var.set(f"Overs: {self.overs}.{self.balls}")
        
    def update_game(self):
        # Update fielder movements
        for fielder in self.fielders:
            if random.random() < 0.02:
                dx = random.randint(-5, 5)
                dy = random.randint(-5, 5)
                self.canvas.move(fielder, dx, dy)
                
        self.root.after(50, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CricketGame()
    game.run()