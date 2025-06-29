import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import requests
from bs4 import BeautifulSoup
import threading

class CollegeFinderBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("College Finder Assistant")
        self.window.geometry("900x700")
        self.window.configure(bg='#2C3E50')
        
        # College database (sample data - you can expand this)
        self.college_data = {
            'bca': [
                {
                    'name': 'Christ University, Bangalore',
                    'ranking': '1',
                    'fees': '₹1.5L - 2L per year',
                    'website': 'https://christuniversity.in',
                    'nirf_rank': 'NIRF Rank: 42'
                },
                {
                    'name': 'Symbiosis Institute of Technology, Pune',
                    'ranking': '2',
                    'fees': '₹2L - 2.5L per year',
                    'website': 'https://www.sitpune.edu.in',
                    'nirf_rank': 'NIRF Rank: 65'
                }
            ],
            'btech': [
                {
                    'name': 'IIT Delhi',
                    'ranking': '1',
                    'fees': '₹2.2L per year',
                    'website': 'https://home.iitd.ac.in',
                    'nirf_rank': 'NIRF Rank: 2'
                }
            ]
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Title
        title_label = tk.Label(self.window, text="College Finder by Degree",
                             font=("Arial", 18, "bold"), bg='#2C3E50', fg='white')
        title_label.pack(pady=10)
        
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                 width=70, height=25,
                                                 bg='#34495E', fg='white',
                                                 font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.window, bg='#2C3E50')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input field
        self.input_field = tk.Entry(input_frame, width=50, font=("Arial", 12))
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind("<Return>", lambda e: self.search_colleges())
        
        # Search button
        search_button = ttk.Button(input_frame, text="Search", command=self.search_colleges)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        
        # Welcome message
        welcome_msg = """
Welcome to College Finder!
Enter a degree (e.g., BCA, BTech, MBA) to find top colleges.
You can also try these commands:
- 'details [college name]' for specific college information
- 'compare [degree]' to compare colleges for a degree
- 'fees [college name]' for fee structure
- 'help' for assistance
        """
        self.add_message("Bot: " + welcome_msg)
        
    def add_message(self, message):
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.see(tk.END)
        
    def search_colleges(self):
        query = self.input_field.get().lower().strip()
        if not query:
            return
            
        self.input_field.delete(0, tk.END)
        self.add_message(f"You: {query}")
        
        if query == 'help':
            self.show_help()
            return
            
        if query.startswith('details '):
            self.show_college_details(query[8:])
            return
            
        if query.startswith('compare '):
            self.compare_colleges(query[8:])
            return
            
        if query.startswith('fees '):
            self.show_fees(query[5:])
            return
        
        # Show progress bar
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Start search in separate thread
        threading.Thread(target=self.fetch_colleges, args=(query,)).start()
        
    def fetch_colleges(self, degree):
        results = []
        degree = degree.lower()
        
        if degree in self.college_data:
            colleges = self.college_data[degree]
            results.append(f"\nTop Colleges for {degree.upper()}:")
            for college in colleges:
                results.append(f"\n🏛️ {college['name']}")
                results.append(f"Ranking: #{college['ranking']}")
                results.append(f"Fees: {college['fees']}")
                results.append(f"{college['nirf_rank']}")
                results.append(f"Website: {college['website']}")
        else:
            results.append(f"\nSorry, no information available for {degree.upper()} at the moment.")
            results.append("Try searching for: BCA, BTech, MBA")
        
        self.window.after(0, self.show_results, results)
        
    def show_results(self, results):
        self.progress.stop()
        self.progress.pack_forget()
        
        for result in results:
            self.add_message(result)
            
    def show_help(self):
        help_text = """
Available Commands:
1. Enter degree name (e.g., BCA, BTech)
2. 'details [college name]' - Get detailed information
3. 'compare [degree]' - Compare colleges for a degree
4. 'fees [college name]' - Get fee structure
5. 'help' - Show this help message
        """
        self.add_message(help_text)
        
    def show_college_details(self, college_name):
        # Add detailed college information display logic here
        self.add_message(f"\nSearching details for: {college_name}")
        # You can add API calls or database queries here
        
    def compare_colleges(self, degree):
        if degree in self.college_data:
            self.add_message(f"\nComparison for {degree.upper()} colleges:")
            colleges = self.college_data[degree]
            for college in colleges:
                self.add_message(f"\n{college['name']}")
                self.add_message(f"NIRF Rank: {college['nirf_rank']}")
                self.add_message(f"Fees: {college['fees']}")
                
    def show_fees(self, college_name):
        self.add_message(f"\nSearching fee structure for: {college_name}")
        # Add fee structure display logic here
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = CollegeFinderBot()
    bot.run()