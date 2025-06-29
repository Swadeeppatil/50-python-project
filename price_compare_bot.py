import tkinter as tk
from tkinter import scrolledtext, ttk
import requests
from bs4 import BeautifulSoup
import threading
import json
import re
from urllib.parse import quote

class PriceCompareBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Price Comparison Assistant")
        self.window.geometry("800x700")
        self.window.configure(bg='#2C3E50')
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Store URLs
        self.stores = {
            'amazon': 'https://www.amazon.in/s?k={}',
            'flipkart': 'https://www.flipkart.com/search?q={}',
            'bigbasket': 'https://www.bigbasket.com/ps/?q={}'
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Title
        title_label = tk.Label(self.window, text="Product Price Comparison",
                             font=("Arial", 16, "bold"), bg='#2C3E50', fg='white')
        title_label.pack(pady=10)
        
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                 width=60, height=25,
                                                 bg='#34495E', fg='white',
                                                 font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.window, bg='#2C3E50')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input field
        self.input_field = tk.Entry(input_frame, width=50, font=("Arial", 12))
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind("<Return>", lambda e: self.search_prices())
        
        # Search button
        search_button = ttk.Button(input_frame, text="Search", command=self.search_prices)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        
        # Welcome message
        self.add_message("Bot: Welcome! Enter a product name to compare prices across stores.")
        
    def add_message(self, message):
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.see(tk.END)
        
    def search_prices(self):
        query = self.input_field.get().strip()
        if not query:
            return
            
        self.input_field.delete(0, tk.END)
        self.add_message(f"You: {query}")
        self.add_message("Bot: Searching prices... Please wait.")
        
        # Show progress bar
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Start search in separate thread
        threading.Thread(target=self.fetch_prices, args=(query,)).start()
        
    def fetch_prices(self, query):
        results = []
        
        # Amazon
        try:
            url = self.stores['amazon'].format(quote(query))
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            price = soup.find('span', class_='a-price-whole')
            if price:
                results.append(f"Amazon: ₹{price.text.strip()}")
        except:
            results.append("Amazon: Price not found")
            
        # Flipkart
        try:
            url = self.stores['flipkart'].format(quote(query))
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            price = soup.find('div', class_='_30jeq3')
            if price:
                results.append(f"Flipkart: {price.text.strip()}")
        except:
            results.append("Flipkart: Price not found")
            
        # BigBasket
        try:
            url = self.stores['bigbasket'].format(quote(query))
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            price = soup.find('span', class_='Price')
            if price:
                results.append(f"BigBasket: {price.text.strip()}")
        except:
            results.append("BigBasket: Price not found")
        
        # Display results
        self.window.after(0, self.show_results, results)
        
    def show_results(self, results):
        self.progress.stop()
        self.progress.pack_forget()
        
        self.add_message("\nPrice Comparison Results:")
        for result in results:
            self.add_message(result)
        self.add_message("\nNote: Prices may vary based on location and availability.")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = PriceCompareBot()
    bot.run()