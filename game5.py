import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
from pathlib import Path

class CricketGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cricket Game")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)

        # Game variables
        self.teams = {
            "India": ["Rohit", "Virat", "Rahul", "Hardik", "Jadeja"],
            "Australia": ["Smith", "Warner", "Maxwell", "Cummins", "Starc"],
            "England": ["Root", "Stokes", "Buttler", "Anderson", "Archer"],
            "New Zealand": ["Williamson", "Conway", "Boult", "Southee", "Santner"]
        }
        
        self.current_score = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.target = 0
        self.batting_team = None
        self.bowling_team = None
        self.current_batsman = None
        self.current_bowler = None
        self.game_phase = "team_selection"  # team_selection, first_innings, second_innings

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_team_selection()

    def show_team_selection(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.main_frame, text="Select Teams", font=('Arial', 20)).pack(pady=20)

        # Team 1 selection
        team1_frame = ttk.LabelFrame(self.main_frame, text="Batting Team")
        team1_frame.pack(pady=10, fill="x")
        
        self.team1_var = tk.StringVar()
        team1_cb = ttk.Combobox(team1_frame, textvariable=self.team1_var, values=list(self.teams.keys()))
        team1_cb.pack(pady=10, padx=10)

        # Team 2 selection
        team2_frame = ttk.LabelFrame(self.main_frame, text="Bowling Team")
        team2_frame.pack(pady=10, fill="x")
        
        self.team2_var = tk.StringVar()
        team2_cb = ttk.Combobox(team2_frame, textvariable=self.team2_var, values=list(self.teams.keys()))
        team2_cb.pack(pady=10, padx=10)

        ttk.Button(self.main_frame, text="Start Match", 
                  command=self.start_match).pack(pady=20)

    def start_match(self):
        if not self.team1_var.get() or not self.team2_var.get():
            messagebox.showerror("Error", "Please select both teams!")
            return
            
        if self.team1_var.get() == self.team2_var.get():
            messagebox.showerror("Error", "Please select different teams!")
            return

        self.batting_team = self.team1_var.get()
        self.bowling_team = self.team2_var.get()
        self.current_batsman = self.teams[self.batting_team][0]
        self.current_bowler = self.teams[self.bowling_team][0]
        self.game_phase = "first_innings"
        self.show_game_screen()

    def show_game_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Score display
        score_frame = ttk.LabelFrame(self.main_frame, text="Score")
        score_frame.pack(fill="x", pady=10)
        
        self.score_label = ttk.Label(score_frame, 
                                   text=f"Score: {self.current_score}/{self.wickets}  Overs: {self.overs}.{self.balls}",
                                   font=('Arial', 16))
        self.score_label.pack(pady=10)

        if self.game_phase == "second_innings":
            target_label = ttk.Label(score_frame, 
                                   text=f"Target: {self.target}",
                                   font=('Arial', 16))
            target_label.pack(pady=5)

        # Player info
        info_frame = ttk.LabelFrame(self.main_frame, text="Current Players")
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, 
                 text=f"Batsman: {self.current_batsman} | Bowler: {self.current_bowler}",
                 font=('Arial', 12)).pack(pady=10)

        # Action buttons
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(pady=20)

        actions = [0, 1, 2, 3, 4, 6, 'W']
        for i, action in enumerate(actions):
            ttk.Button(action_frame, text=str(action), 
                      command=lambda x=action: self.process_ball(x)).pack(side=tk.LEFT, padx=5)

    def process_ball(self, outcome):
        if outcome == 'W':
            self.wickets += 1
            if self.wickets < 5:  # Assuming 5 wickets per team
                self.current_batsman = self.teams[self.batting_team][self.wickets]
            else:
                self.end_innings()
                return
        else:
            self.current_score += outcome

        self.balls += 1
        if self.balls == 6:
            self.balls = 0
            self.overs += 1
            self.current_bowler = random.choice(self.teams[self.bowling_team])

        if self.overs >= 5:  # 5 overs per innings
            self.end_innings()
            return

        if self.game_phase == "second_innings":
            if self.current_score >= self.target:
                self.end_game(self.batting_team)
                return
            elif self.wickets >= 5:
                self.end_game(self.bowling_team)
                return

        self.score_label.config(text=f"Score: {self.current_score}/{self.wickets}  Overs: {self.overs}.{self.balls}")

    def end_innings(self):
        if self.game_phase == "first_innings":
            self.target = self.current_score + 1
            self.current_score = 0
            self.wickets = 0
            self.overs = 0
            self.balls = 0
            self.game_phase = "second_innings"
            
            # Swap teams
            self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
            self.current_batsman = self.teams[self.batting_team][0]
            self.current_bowler = self.teams[self.bowling_team][0]
            
            messagebox.showinfo("Innings End", 
                              f"First innings complete!\nTarget: {self.target}")
            self.show_game_screen()
        else:
            self.end_game(self.bowling_team)

    def end_game(self, winner):
        messagebox.showinfo("Game Over", f"{winner} wins!")
        if messagebox.askyesno("Play Again", "Would you like to play another match?"):
            self.__init__()
        else:
            self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = CricketGame()
    game.run()