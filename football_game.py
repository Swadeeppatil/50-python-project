import tkinter as tk
import random
import math

class FootballGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Football Game")
        self.root.geometry("1000x600")
        
        # Game canvas
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg='green')
        self.canvas.pack()
        
        # Game variables
        self.score_team1 = 0
        self.score_team2 = 0
        self.ball_x = 500
        self.ball_y = 300
        self.ball_dx = 0
        self.ball_dy = 0
        self.player_speed = 5
        self.game_over = False
        
        # Create field
        self.create_field()
        
        # Create players
        self.create_players()
        
        # Create ball
        self.create_ball()
        
        # Create scoreboard
        self.create_scoreboard()
        
        # Key bindings
        self.setup_controls()
        
        # Start game loop
        self.update_game()
        
    def create_field(self):
        # Draw field lines
        self.canvas.create_rectangle(50, 50, 950, 550, outline='white', width=2)
        self.canvas.create_line(500, 50, 500, 550, fill='white', width=2)
        self.canvas.create_oval(450, 250, 550, 350, outline='white', width=2)
        
        # Draw goals
        self.canvas.create_rectangle(30, 250, 50, 350, fill='white', outline='white')
        self.canvas.create_rectangle(950, 250, 970, 350, fill='white', outline='white')
        
    def create_players(self):
        # Team 1 (Blue)
        self.player1 = self.canvas.create_oval(200, 300, 220, 320, fill='blue', tags='player1')
        self.goalkeeper1 = self.canvas.create_oval(70, 290, 90, 310, fill='blue', tags='keeper1')
        
        # Team 2 (Red)
        self.player2 = self.canvas.create_oval(780, 300, 800, 320, fill='red', tags='player2')
        self.goalkeeper2 = self.canvas.create_oval(910, 290, 930, 310, fill='red', tags='keeper2')
        
    def create_ball(self):
        self.ball = self.canvas.create_oval(
            self.ball_x-10, self.ball_y-10,
            self.ball_x+10, self.ball_y+10,
            fill='white'
        )
        
    def create_scoreboard(self):
        self.score_text = self.canvas.create_text(
            500, 30,
            text=f"Blue {self.score_team1} - {self.score_team2} Red",
            fill='white',
            font=('Arial', 20)
        )
        
    def setup_controls(self):
        # Team 1 controls
        self.root.bind('w', lambda e: self.move_player(self.player1, 0, -self.player_speed))
        self.root.bind('s', lambda e: self.move_player(self.player1, 0, self.player_speed))
        self.root.bind('a', lambda e: self.move_player(self.player1, -self.player_speed, 0))
        self.root.bind('d', lambda e: self.move_player(self.player1, self.player_speed, 0))
        self.root.bind('f', lambda e: self.kick_ball(self.player1))
        
        # Team 2 controls
        self.root.bind('<Up>', lambda e: self.move_player(self.player2, 0, -self.player_speed))
        self.root.bind('<Down>', lambda e: self.move_player(self.player2, 0, self.player_speed))
        self.root.bind('<Left>', lambda e: self.move_player(self.player2, -self.player_speed, 0))
        self.root.bind('<Right>', lambda e: self.move_player(self.player2, self.player_speed, 0))
        self.root.bind('<space>', lambda e: self.kick_ball(self.player2))
        
    def move_player(self, player, dx, dy):
        x1, y1, x2, y2 = self.canvas.coords(player)
        if (50 < x1 + dx and x2 + dx < 950 and 
            50 < y1 + dy and y2 + dy < 550):
            self.canvas.move(player, dx, dy)
            
    def kick_ball(self, player):
        player_coords = self.canvas.coords(player)
        player_x = (player_coords[0] + player_coords[2]) / 2
        player_y = (player_coords[1] + player_coords[3]) / 2
        
        # Calculate distance to ball
        distance = math.sqrt((player_x - self.ball_x)**2 + (player_y - self.ball_y)**2)
        
        if distance < 30:  # Kick range
            # Calculate kick direction
            angle = math.atan2(self.ball_y - player_y, self.ball_x - player_x)
            self.ball_dx = math.cos(angle) * -10
            self.ball_dy = math.sin(angle) * -10
            
    def update_ball_position(self):
        # Update ball position
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball friction
        self.ball_dx *= 0.98
        self.ball_dy *= 0.98
        
        # Ball collision with walls
        if self.ball_x < 60 or self.ball_x > 940:
            if 250 < self.ball_y < 350:  # Goal!
                self.score_goal()
            self.ball_dx *= -1
            
        if self.ball_y < 60 or self.ball_y > 540:
            self.ball_dy *= -1
            
        # Update ball position on canvas
        self.canvas.coords(
            self.ball,
            self.ball_x-10, self.ball_y-10,
            self.ball_x+10, self.ball_y+10
        )
        
    def score_goal(self):
        if self.ball_x < 500:
            self.score_team2 += 1
        else:
            self.score_team1 += 1
            
        # Update scoreboard
        self.canvas.itemconfig(
            self.score_text,
            text=f"Blue {self.score_team1} - {self.score_team2} Red"
        )
        
        # Reset ball position
        self.ball_x = 500
        self.ball_y = 300
        self.ball_dx = 0
        self.ball_dy = 0
        
        if self.score_team1 >= 5 or self.score_team2 >= 5:
            self.game_over = True
            self.show_game_over()
            
    def show_game_over(self):
        winner = "Blue" if self.score_team1 > self.score_team2 else "Red"
        self.canvas.create_text(
            500, 300,
            text=f"Game Over!\n{winner} team wins!",
            fill='white',
            font=('Arial', 30)
        )
        
    def update_goalkeeper_ai(self):
        # Simple AI for goalkeepers
        for keeper, goal_x in [(self.goalkeeper1, 70), (self.goalkeeper2, 910)]:
            keeper_coords = self.canvas.coords(keeper)
            keeper_y = (keeper_coords[1] + keeper_coords[3]) / 2
            
            if abs(self.ball_x - goal_x) < 200:  # Only move when ball is close
                if self.ball_y > keeper_y + 10:
                    self.move_player(keeper, 0, 2)
                elif self.ball_y < keeper_y - 10:
                    self.move_player(keeper, 0, -2)
                    
    def update_game(self):
        if not self.game_over:
            self.update_ball_position()
            self.update_goalkeeper_ai()
            
        self.root.after(16, self.update_game)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = FootballGame()
    game.run()

"""
- Save as football_game.py
- Run the file
- Controls:
- Team 1 (Blue):
  - W/A/S/D: Move
  - F: Kick ball
- Team 2 (Red):
  - Arrow keys: Move
  - Space: Kick ball
"""