import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np
from datetime import datetime
import re
import json

class WebDataAnalyzer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Web Data Analyzer")
        self.window.geometry("1400x900")
        self.window.configure(bg='#2C3E50')
        
        self.df = None
        self.scraped_data = {}
        self.create_gui()
        
    def create_gui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Panel - Data Collection
        left_panel = ttk.LabelFrame(main_frame, text="Data Collection")
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        # URL and scraping options
        ttk.Label(left_panel, text="Website URL:").pack(anchor='w', pady=2)
        self.url_entry = ttk.Entry(left_panel)
        self.url_entry.pack(fill='x', pady=2, padx=5)
        
        # Scraping options
        options_frame = ttk.LabelFrame(left_panel, text="Scraping Options")
        options_frame.pack(fill='x', pady=5, padx=5)
        
        self.scrape_vars = {
            'Reviews': tk.BooleanVar(value=True),
            'Ratings': tk.BooleanVar(value=True),
            'Prices': tk.BooleanVar(value=True),
            'Visits': tk.BooleanVar(value=True),
            'Sales': tk.BooleanVar(value=True)
        }
        
        for option, var in self.scrape_vars.items():
            ttk.Checkbutton(options_frame, text=option, variable=var).pack(anchor='w')
        
        ttk.Button(left_panel, text="Scrape Data", 
                  command=self.scrape_data).pack(fill='x', pady=5, padx=5)
        
        # Data display
        self.data_display = scrolledtext.ScrolledText(left_panel, height=20)
        self.data_display.pack(fill='both', expand=True, pady=5, padx=5)
        
        # Right Panel - Analysis
        right_panel = ttk.LabelFrame(main_frame, text="Analysis Tools")
        right_panel.pack(side='right', fill='both', padx=5)
        
        # Analysis options
        analysis_frame = ttk.LabelFrame(right_panel, text="Analysis Options")
        analysis_frame.pack(fill='x', pady=5, padx=5)
        
        analysis_buttons = [
            ("Review Analysis", self.analyze_reviews),
            ("Rating Distribution", self.analyze_ratings),
            ("Price Trends", self.analyze_prices),
            ("Visit Statistics", self.analyze_visits),
            ("Sales Performance", self.analyze_sales),
            ("Save Analysis", self.save_analysis)
        ]
        
        for text, command in analysis_buttons:
            ttk.Button(analysis_frame, text=text, 
                      command=command).pack(fill='x', pady=2)
        
        # Graph area
        self.graph_frame = ttk.LabelFrame(right_panel, text="Visualization")
        self.graph_frame.pack(fill='both', expand=True, pady=5)
        
    def scrape_data(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL!")
            return
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            self.scraped_data = {}
            
            if self.scrape_vars['Reviews'].get():
                reviews = soup.find_all(class_=re.compile('review|comment'))
                self.scraped_data['reviews'] = [r.text.strip() for r in reviews]
            
            if self.scrape_vars['Ratings'].get():
                ratings = soup.find_all(class_=re.compile('rating|stars'))
                self.scraped_data['ratings'] = [self.extract_rating(r.text) for r in ratings]
            
            if self.scrape_vars['Prices'].get():
                prices = soup.find_all(class_=re.compile('price'))
                self.scraped_data['prices'] = [self.extract_price(p.text) for p in prices]
            
            if self.scrape_vars['Visits'].get():
                visits = soup.find_all(class_=re.compile('views|visits'))
                self.scraped_data['visits'] = [self.extract_number(v.text) for v in visits]
            
            if self.scrape_vars['Sales'].get():
                sales = soup.find_all(class_=re.compile('sales|sold'))
                self.scraped_data['sales'] = [self.extract_number(s.text) for s in sales]
            
            self.display_scraped_data()
            messagebox.showinfo("Success", "Data scraped successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape data: {str(e)}")
    
    def extract_rating(self, text):
        try:
            return float(re.search(r'\d+\.?\d*', text).group())
        except:
            return 0
    
    def extract_price(self, text):
        try:
            return float(re.search(r'\d+\.?\d*', text).group())
        except:
            return 0
    
    def extract_number(self, text):
        try:
            return int(re.search(r'\d+', text).group())
        except:
            return 0
    
    def display_scraped_data(self):
        self.data_display.delete(1.0, tk.END)
        for category, data in self.scraped_data.items():
            self.data_display.insert(tk.END, f"\n{category.upper()}:\n")
            self.data_display.insert(tk.END, str(data[:10]) + "...\n")
    
    def analyze_reviews(self):
        if 'reviews' not in self.scraped_data:
            messagebox.showwarning("Warning", "No review data available!")
            return
        
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'perfect']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible']
        
        sentiments = []
        for review in self.scraped_data['reviews']:
            review = review.lower()
            pos_count = sum(1 for word in positive_words if word in review)
            neg_count = sum(1 for word in negative_words if word in review)
            sentiments.append('Positive' if pos_count > neg_count else 'Negative')
        
        sentiment_counts = pd.Series(sentiments).value_counts()
        
        plt.figure(figsize=(8, 6))
        sentiment_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Review Sentiment Distribution')
        self.display_plot()
    
    def analyze_ratings(self):
        if 'ratings' not in self.scraped_data:
            messagebox.showwarning("Warning", "No rating data available!")
            return
        
        ratings = pd.Series(self.scraped_data['ratings'])
        plt.figure(figsize=(8, 6))
        ratings.hist(bins=5)
        plt.title('Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Frequency')
        self.display_plot()
    
    def analyze_prices(self):
        if 'prices' not in self.scraped_data:
            messagebox.showwarning("Warning", "No price data available!")
            return
        
        prices = pd.Series(self.scraped_data['prices'])
        plt.figure(figsize=(8, 6))
        sns.boxplot(y=prices)
        plt.title('Price Distribution')
        plt.ylabel('Price')
        self.display_plot()
    
    def analyze_visits(self):
        if 'visits' not in self.scraped_data:
            messagebox.showwarning("Warning", "No visit data available!")
            return
        
        visits = pd.Series(self.scraped_data['visits'])
        plt.figure(figsize=(8, 6))
        visits.plot(kind='line')
        plt.title('Visit Trends')
        plt.xlabel('Item Index')
        plt.ylabel('Number of Visits')
        self.display_plot()
    
    def analyze_sales(self):
        if 'sales' not in self.scraped_data:
            messagebox.showwarning("Warning", "No sales data available!")
            return
        
        sales = pd.Series(self.scraped_data['sales'])
        plt.figure(figsize=(8, 6))
        sales.plot(kind='bar')
        plt.title('Sales Performance')
        plt.xlabel('Item Index')
        plt.ylabel('Number of Sales')
        plt.xticks(rotation=45)
        self.display_plot()
    
    def save_analysis(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"),
                      ("CSV files", "*.csv"),
                      ("Text files", "*.txt")])
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=4)
                messagebox.showinfo("Success", "Analysis saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save analysis: {str(e)}")
    
    def display_plot(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WebDataAnalyzer()
    app.run()