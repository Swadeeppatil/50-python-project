import tkinter as tk
from tkinter import messagebox
import random
import time

class WWEFightingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WWE Fighting Game")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)

        # Game variables
        self.player1_health = 100
        self.player2_health = 100
        self.game_over = False
        self.current_turn = 1

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg='black')
        self.canvas.pack()

        # Create wrestling ring
        self.create_ring()

        # Create wrestlers
        self.player1 = self.canvas.create_rectangle(200, 300, 280, 450, fill='red', tags='player1')
        self.player2 = self.canvas.create_rectangle(700, 300, 780, 450, fill='blue', tags='player2')

        # Health bars
        self.create_health_bars()

        # Move controls
        self.moves = {
            'punch': 10,
            'kick': 15,
            'special': 25
        }

        # Create buttons
        self.create_control_buttons()

        # Bind keyboard controls
        self.setup_keyboard_controls()

        # Animation variables
        self.is_animating = False
        self.animation_step = 0

    def create_ring(self):
        # Ring floor
        self.canvas.create_rectangle(100, 450, 900, 500, fill='gray')
        # Ring ropes
        self.canvas.create_line(100, 300, 900, 300, fill='white', width=5)
        self.canvas.create_line(100, 350, 900, 350, fill='white', width=5)
        # Ring posts
        self.canvas.create_rectangle(90, 280, 110, 500, fill='silver')
        self.canvas.create_rectangle(890, 280, 910, 500, fill='silver')

    def create_health_bars(self):
        # Player 1 health bar
        self.canvas.create_text(200, 50, text="Player 1", fill='white', font=('Arial', 20))
        self.p1_health_bar = self.canvas.create_rectangle(100, 70, 300, 90, fill='green')
        
        # Player 2 health bar
        self.canvas.create_text(800, 50, text="Player 2", fill='white', font=('Arial', 20))
        self.p2_health_bar = self.canvas.create_rectangle(700, 70, 900, 90, fill='green')

    def create_control_buttons(self):
        # Player 1 controls
        tk.Button(self.root, text="Punch (A)", command=lambda: self.perform_move(1, 'punch')).place(x=50, y=520)
        tk.Button(self.root, text="Kick (S)", command=lambda: self.perform_move(1, 'kick')).place(x=150, y=520)
        tk.Button(self.root, text="Special (D)", command=lambda: self.perform_move(1, 'special')).place(x=250, y=520)

        # Player 2 controls
        tk.Button(self.root, text="Punch (J)", command=lambda: self.perform_move(2, 'punch')).place(x=650, y=520)
        tk.Button(self.root, text="Kick (K)", command=lambda: self.perform_move(2, 'kick')).place(x=750, y=520)
        tk.Button(self.root, text="Special (L)", command=lambda: self.perform_move(2, 'special')).place(x=850, y=520)

    def setup_keyboard_controls(self):
        # Player 1 controls
        self.root.bind('a', lambda event: self.perform_move(1, 'punch'))
        self.root.bind('s', lambda event: self.perform_move(1, 'kick'))
        self.root.bind('d', lambda event: self.perform_move(1, 'special'))

        # Player 2 controls
        self.root.bind('j', lambda event: self.perform_move(2, 'punch'))
        self.root.bind('k', lambda event: self.perform_move(2, 'kick'))
        self.root.bind('l', lambda event: self.perform_move(2, 'special'))

    def perform_move(self, player, move_type):
        if self.game_over or self.is_animating:
            return

        if (player == 1 and self.current_turn == 2) or (player == 2 and self.current_turn == 1):
            messagebox.showinfo("Wrong Turn", "It's not your turn!")
            return

        self.is_animating = True
        damage = self.moves[move_type]
        
        # Add some randomness to damage
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))

        if player == 1:
            self.animate_attack(self.player1, self.player2, damage)
            self.player2_health -= damage
        else:
            self.animate_attack(self.player2, self.player1, damage)
            self.player1_health -= damage

        self.update_health_bars()
        self.current_turn = 2 if self.current_turn == 1 else 1

    def animate_attack(self, attacker, target, damage):
        if self.animation_step < 5:
            # Move attacker towards target
            if int(self.canvas.coords(attacker)[0]) < int(self.canvas.coords(target)[0]):
                self.canvas.move(attacker, 20, 0)
            else:
                self.canvas.move(attacker, -20, 0)
            
            self.animation_step += 1
            self.root.after(50, lambda: self.animate_attack(attacker, target, damage))
        else:
            # Show damage text
            x = self.canvas.coords(target)[0]
            y = self.canvas.coords(target)[1]
            damage_text = self.canvas.create_text(x, y-20, text=f"-{damage}", fill='red', font=('Arial', 16))
            
            # Reset attacker position
            if attacker == self.player1:
                self.canvas.coords(attacker, 200, 300, 280, 450)
            else:
                self.canvas.coords(attacker, 700, 300, 780, 450)
            
            self.animation_step = 0
            self.is_animating = False
            
            # Remove damage text after a delay
            self.root.after(1000, lambda: self.canvas.delete(damage_text))
            
            self.check_game_over()

    def update_health_bars(self):
        # Ensure health doesn't go below 0
        self.player1_health = max(0, self.player1_health)
        self.player2_health = max(0, self.player2_health)

        # Update health bar widths
        self.canvas.coords(self.p1_health_bar, 100, 70, 100 + (self.player1_health * 2), 90)
        self.canvas.coords(self.p2_health_bar, 700, 70, 700 + (self.player2_health * 2), 90)

        # Update health bar colors
        for player, health, health_bar in [(1, self.player1_health, self.p1_health_bar), 
                                         (2, self.player2_health, self.p2_health_bar)]:
            if health > 60:
                color = 'green'
            elif health > 30:
                color = 'yellow'
            else:
                color = 'red'
            self.canvas.itemconfig(health_bar, fill=color)

    def check_game_over(self):
        if self.player1_health <= 0 or self.player2_health <= 0:
            self.game_over = True
            winner = "Player 2" if self.player1_health <= 0 else "Player 1"
            self.show_game_over(winner)

    def show_game_over(self, winner):
        self.canvas.create_text(500, 250, text=f"{winner} Wins!", 
                              fill='yellow', font=('Arial', 36))
        if messagebox.askyesno("Game Over", f"{winner} Wins!\nPlay again?"):
            self.reset_game()
        else:
            self.root.quit()

    def reset_game(self):
        self.player1_health = 100
        self.player2_health = 100
        self.game_over = False
        self.current_turn = 1
        self.update_health_bars()
        self.canvas.delete("text")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = WWEFightingGame()
    game.run()

"""
Controls:
- Player 1: A (Punch), S (Kick), D (Special Move)
- Player 2: J (Punch), K (Kick), L (Special Move)


"""