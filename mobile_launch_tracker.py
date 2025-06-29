import tkinter as tk
from tkinter import scrolledtext, ttk
import json
from datetime import datetime

class MobileLaunchBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Mobile Launch Tracker India")
        self.window.geometry("1000x700")
        self.window.configure(bg='#1E1E1E')
        
        # Mobile launch database
        self.mobile_data = {
            '2023': {
                'realme': [
                    {
                        'model': 'Realme 11 Pro+ 5G',
                        'launch_date': 'June 2023',
                        'price': '₹27,999',
                        'specs': {
                            'display': '6.7" AMOLED',
                            'processor': 'Dimensity 7050',
                            'camera': '200MP + 8MP + 2MP',
                            'battery': '5000mAh'
                        }
                    },
                    {
                        'model': 'Realme Narzo 60 Pro 5G',
                        'launch_date': 'July 2023',
                        'price': '₹23,999',
                        'specs': {
                            'display': '6.7" AMOLED',
                            'processor': 'Dimensity 7050',
                            'camera': '100MP + 2MP',
                            'battery': '5000mAh'
                        }
                    }
                ],
                'samsung': [
                    {
                        'model': 'Samsung Galaxy S23 Ultra',
                        'launch_date': 'February 2023',
                        'price': '₹1,24,999',
                        'specs': {
                            'display': '6.8" Dynamic AMOLED',
                            'processor': 'Snapdragon 8 Gen 2',
                            'camera': '200MP + 10MP + 10MP + 12MP',
                            'battery': '5000mAh'
                        }
                    }
                ]
            }
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Title Frame
        title_frame = tk.Frame(self.window, bg='#1E1E1E')
        title_frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(title_frame, text="📱 Mobile Launch Tracker India",
                        font=("Helvetica", 24, "bold"), bg='#1E1E1E', fg='#00FF00')
        title.pack()
        
        # Control Panel
        control_frame = tk.Frame(self.window, bg='#2D2D2D')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Year Selection
        tk.Label(control_frame, text="Select Year:", bg='#2D2D2D', fg='white',
                font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        
        years = [str(year) for year in range(2007, 2026)]
        self.year_var = tk.StringVar()
        year_menu = ttk.Combobox(control_frame, textvariable=self.year_var,
                               values=years, width=10)
        year_menu.pack(side=tk.LEFT, padx=5)
        year_menu.set("2023")
        
        # Company Selection
        tk.Label(control_frame, text="Select Company:", bg='#2D2D2D', fg='white',
                font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        
        self.companies = ['Realme', 'Samsung', 'Xiaomi', 'OnePlus', 'Vivo', 'OPPO', 'iQOO', 'Nothing']
        self.company_var = tk.StringVar()
        company_menu = ttk.Combobox(control_frame, textvariable=self.company_var,
                                  values=self.companies, width=15)
        company_menu.pack(side=tk.LEFT, padx=5)
        
        # Search Button
        ttk.Button(control_frame, text="Search",
                  command=self.show_launches).pack(side=tk.LEFT, padx=10)
        
        # Display Area
        self.display_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                    width=80, height=30,
                                                    bg='#2D2D2D', fg='white',
                                                    font=("Courier", 11))
        self.display_area.pack(padx=10, pady=10)
        
        # Welcome Message
        welcome_text = """
📱 Welcome to Mobile Launch Tracker India!

Track smartphone launches in India:
• Select year (2007-2025)
• Choose mobile company
• Get detailed specifications
• View launch dates
• Compare prices
• Check features

Select year and company, then click Search to begin.
        """
        self.add_message(welcome_text)
        
    def add_message(self, message):
        self.display_area.insert(tk.END, message + "\n")
        self.display_area.see(tk.END)
        
    def show_launches(self):
        year = self.year_var.get()
        company = self.company_var.get().lower()
        
        self.display_area.delete(1.0, tk.END)
        
        if not company:
            self.add_message("Please select a company!")
            return
            
        self.add_message(f"🔍 Searching for {company.upper()} launches in {year}...\n")
        
        if year in self.mobile_data and company in self.mobile_data[year]:
            phones = self.mobile_data[year][company]
            self.add_message(f"Found {len(phones)} models:\n")
            
            for phone in phones:
                self.add_message("=" * 50)
                self.add_message(f"📱 Model: {phone['model']}")
                self.add_message(f"📅 Launch Date: {phone['launch_date']}")
                self.add_message(f"💰 Price: {phone['price']}")
                self.add_message("\n📊 Specifications:")
                for spec, value in phone['specs'].items():
                    self.add_message(f"• {spec.title()}: {value}")
                self.add_message("=" * 50 + "\n")
        else:
            self.add_message(f"No launches found for {company.upper()} in {year}")
            self.add_message("Try a different year or company")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = MobileLaunchBot()
    bot.run()