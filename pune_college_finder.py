import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import threading
import webbrowser

class PuneCollegeBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pune College Finder")
        self.window.geometry("1000x700")
        self.window.configure(bg='#2C3E50')
        
        # Pune College Database
        self.pune_colleges = {
            'bca': [
                {
                    'name': 'Symbiosis Institute of Technology',
                    'location': 'Viman Nagar',
                    'fees': '₹2.2L per year',
                    'rating': '4.5/5',
                    'website': 'www.sitpune.edu.in',
                    'cutoff': '80%',
                    'seats': 120,
                    'placement': '95%'
                },
                {
                    'name': 'Pune Institute of Computer Technology',
                    'location': 'Dhankawadi',
                    'fees': '₹1.5L per year',
                    'rating': '4.3/5',
                    'website': 'www.pict.edu',
                    'cutoff': '75%',
                    'seats': 60,
                    'placement': '90%'
                }
            ],
            'btech': [
                {
                    'name': 'College of Engineering Pune (COEP)',
                    'location': 'Shivajinagar',
                    'fees': '₹1.45L per year',
                    'rating': '4.8/5',
                    'website': 'www.coep.org.in',
                    'cutoff': 'JEE: 98%ile',
                    'seats': 540,
                    'placement': '98%'
                },
                {
                    'name': 'VIT Pune',
                    'location': 'Upper Indira Nagar',
                    'fees': '₹1.8L per year',
                    'rating': '4.4/5',
                    'website': 'www.vit.edu',
                    'cutoff': 'JEE: 85%ile',
                    'seats': 480,
                    'placement': '92%'
                }
            ],
            'mba': [
                {
                    'name': 'Symbiosis Institute of Business Management',
                    'location': 'Lavale',
                    'fees': '₹21L total',
                    'rating': '4.7/5',
                    'website': 'www.sibm.edu',
                    'cutoff': 'CAT: 95%ile',
                    'seats': 180,
                    'placement': '100%'
                }
            ]
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Title Frame
        title_frame = tk.Frame(self.window, bg='#2C3E50')
        title_frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(title_frame, text="Pune College Explorer",
                        font=("Helvetica", 24, "bold"), bg='#2C3E50', fg='white')
        title.pack()
        
        # Left Panel - Search Options
        left_panel = tk.Frame(self.window, bg='#34495E')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Degree Selection
        tk.Label(left_panel, text="Select Degree:", bg='#34495E', fg='white',
                font=("Helvetica", 12)).pack(pady=5)
        
        self.degrees = ['BCA', 'BTech', 'MBA', 'MCA', 'BBA', 'BSc', 'BCom']
        self.degree_var = tk.StringVar()
        degree_menu = ttk.Combobox(left_panel, textvariable=self.degree_var,
                                 values=self.degrees, width=15)
        degree_menu.pack(pady=5)
        
        # Filters
        tk.Label(left_panel, text="Filters:", bg='#34495E', fg='white',
                font=("Helvetica", 12)).pack(pady=5)
        
        self.fee_var = tk.BooleanVar()
        ttk.Checkbutton(left_panel, text="Low to High Fees",
                       variable=self.fee_var).pack()
        
        self.rating_var = tk.BooleanVar()
        ttk.Checkbutton(left_panel, text="High Rating",
                       variable=self.rating_var).pack()
        
        ttk.Button(left_panel, text="Search",
                   command=self.search_colleges).pack(pady=10)
        
        # Right Panel - Results
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                width=80, height=35,
                                                bg='#34495E', fg='white',
                                                font=("Helvetica", 11))
        self.chat_area.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Welcome Message
        welcome_text = """
Welcome to Pune College Explorer! 🎓

Find the best colleges in Pune for your desired degree.
Features:
• Comprehensive college information
• Real-time placement data
• Fee structures
• Admission criteria
• Campus details

Select a degree from the dropdown and click Search to begin.
        """
        self.add_message(welcome_text)
        
    def add_message(self, message):
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.see(tk.END)
        
    def search_colleges(self):
        degree = self.degree_var.get().lower()
        self.chat_area.delete(1.0, tk.END)
        
        if not degree:
            self.add_message("Please select a degree first!")
            return
            
        self.add_message(f"🔍 Searching colleges for {degree.upper()} in Pune...\n")
        
        if degree in self.pune_colleges:
            colleges = self.pune_colleges[degree]
            
            # Apply filters
            if self.fee_var.get():
                colleges = sorted(colleges, key=lambda x: float(x['fees'].split('L')[0][1:]))
            if self.rating_var.get():
                colleges = sorted(colleges, key=lambda x: float(x['rating'].split('/')[0]), reverse=True)
            
            for college in colleges:
                self.add_message("=" * 50)
                self.add_message(f"🏛️ {college['name']}")
                self.add_message(f"📍 Location: {college['location']}")
                self.add_message(f"💰 Fees: {college['fees']}")
                self.add_message(f"⭐ Rating: {college['rating']}")
                self.add_message(f"📊 Cutoff: {college['cutoff']}")
                self.add_message(f"👥 Total Seats: {college['seats']}")
                self.add_message(f"💼 Placement: {college['placement']}")
                self.add_message(f"🌐 Website: {college['website']}")
                self.add_message("=" * 50 + "\n")
        else:
            self.add_message(f"No data available for {degree.upper()} programs in Pune.")
            self.add_message("Available degrees: BCA, BTech, MBA")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = PuneCollegeBot()
    bot.run()