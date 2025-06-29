import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import threading
import requests
from datetime import datetime

class LiveScoreBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Live Sports Score Bot")
        self.window.geometry("1000x700")
        self.window.configure(bg='#1A1A1A')
        
        # Sample match data (replace with real API data)
        self.matches = {
            'cricket': [
                {
                    'teams': 'India vs Australia',
                    'venue': 'MCG, Melbourne',
                    'time': '09:00 AM IST',
                    'score': 'IND: 285/4 (45.2 ov) | AUS: Yet to bat',
                    'status': 'Live',
                    'players': {
                        'India': ['Rohit Sharma (C)', 'Virat Kohli', 'KL Rahul'],
                        'Australia': ['Pat Cummins (C)', 'Steve Smith', 'Mitchell Starc']
                    },
                    'recent': ['1', '4', '6', 'W', '2']
                }
            ],
            'football': [
                {
                    'teams': 'Manchester City vs Liverpool',
                    'venue': 'Etihad Stadium, Manchester',
                    'time': '8:30 PM BST',
                    'score': 'MCI 2 - 1 LIV',
                    'status': 'Live - 75min',
                    'players': {
                        'Manchester City': ['Haaland', 'De Bruyne', 'Ederson'],
                        'Liverpool': ['Salah', 'Van Dijk', 'Alisson']
                    },
                    'recent': ['Goal!', 'Yellow Card', 'Corner']
                }
            ]
        }
        
        self.create_gui()
        self.start_score_update()
        
    def create_gui(self):
        # Title Frame
        title_frame = tk.Frame(self.window, bg='#1A1A1A')
        title_frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(title_frame, text="🏆 Live Sports Score",
                        font=("Helvetica", 24, "bold"), bg='#1A1A1A', fg='#00FF00')
        title.pack()
        
        # Left Panel - Sport Selection
        left_panel = tk.Frame(self.window, bg='#2A2A2A')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        tk.Label(left_panel, text="Select Sport:", bg='#2A2A2A', fg='white',
                font=("Helvetica", 12, "bold")).pack(pady=5)
        
        self.sports = ['Cricket', 'Football']
        self.sport_var = tk.StringVar()
        sport_menu = ttk.Combobox(left_panel, textvariable=self.sport_var,
                                values=self.sports, width=15)
        sport_menu.pack(pady=5)
        sport_menu.set("Select Sport")
        
        # Buttons
        ttk.Button(left_panel, text="Show Live Matches",
                  command=self.show_matches).pack(pady=5)
        ttk.Button(left_panel, text="Show Players",
                  command=self.show_players).pack(pady=5)
        ttk.Button(left_panel, text="Recent Updates",
                  command=self.show_recent).pack(pady=5)
        
        # Main Display Area
        self.display_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                    width=80, height=35,
                                                    bg='#2A2A2A', fg='white',
                                                    font=("Courier", 11))
        self.display_area.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Welcome Message
        welcome_text = """
🎮 Welcome to Live Sports Score Bot! 

Get real-time updates for:
• Live match scores
• Team lineups
• Match venues
• Recent events
• Player statistics

Select a sport from the dropdown and click any button to begin.
        """
        self.add_message(welcome_text)
        
    def add_message(self, message):
        self.display_area.insert(tk.END, message + "\n")
        self.display_area.see(tk.END)
        
    def show_matches(self):
        sport = self.sport_var.get().lower()
        self.display_area.delete(1.0, tk.END)
        
        if not sport or sport == "select sport":
            self.add_message("Please select a sport first!")
            return
            
        if sport in self.matches:
            self.add_message(f"🏟️ Live {sport.title()} Matches:\n")
            for match in self.matches[sport]:
                self.add_message("=" * 50)
                self.add_message(f"⚡ {match['teams']}")
                self.add_message(f"📍 Venue: {match['venue']}")
                self.add_message(f"⏰ Time: {match['time']}")
                self.add_message(f"📊 Score: {match['score']}")
                self.add_message(f"📌 Status: {match['status']}")
                self.add_message("=" * 50 + "\n")
                
    def show_players(self):
        sport = self.sport_var.get().lower()
        self.display_area.delete(1.0, tk.END)
        
        if sport in self.matches:
            for match in self.matches[sport]:
                self.add_message(f"👥 Playing XI - {match['teams']}\n")
                for team, players in match['players'].items():
                    self.add_message(f"\n{team}:")
                    for player in players:
                        self.add_message(f"• {player}")
                    self.add_message("")
                    
    def show_recent(self):
        sport = self.sport_var.get().lower()
        self.display_area.delete(1.0, tk.END)
        
        if sport in self.matches:
            for match in self.matches[sport]:
                self.add_message(f"📱 Recent Updates - {match['teams']}\n")
                self.add_message("Last 5 events:")
                for event in match['recent']:
                    self.add_message(f"➤ {event}")
                    
    def start_score_update(self):
        def update():
            # Simulate real-time updates (replace with actual API calls)
            threading.Timer(30.0, update).start()
            # Update scores here using real API
            
        update()
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = LiveScoreBot()
    bot.run()