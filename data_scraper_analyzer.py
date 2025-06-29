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
import json

class DataScraperAnalyzer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Data Scraper & Analyzer")
        self.window.geometry("1400x900")
        self.window.configure(bg='#2C3E50')
        
        self.df = None
        self.scraped_data = None
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Panel
        left_panel = ttk.LabelFrame(main_frame, text="Data Collection")
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        # URL input
        url_frame = ttk.Frame(left_panel)
        url_frame.pack(fill='x', pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side='left', padx=5)
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(url_frame, text="Scrape", command=self.scrape_data).pack(side='right', padx=5)
        
        # Data display
        self.data_display = scrolledtext.ScrolledText(left_panel, height=20)
        self.data_display.pack(fill='both', expand=True, pady=5)
        
        # Right Panel - Analysis Tools
        right_panel = ttk.LabelFrame(main_frame, text="Data Analysis")
        right_panel.pack(side='right', fill='both', padx=5)
        
        # Analysis controls
        controls_frame = ttk.Frame(right_panel)
        controls_frame.pack(fill='x', pady=5)
        
        # Column selection
        ttk.Label(controls_frame, text="Select Columns:").pack(anchor='w', pady=2)
        self.x_col = ttk.Combobox(controls_frame, width=15)
        self.x_col.pack(fill='x', pady=2)
        self.y_col = ttk.Combobox(controls_frame, width=15)
        self.y_col.pack(fill='x', pady=2)
        
        # Analysis buttons
        analysis_frame = ttk.LabelFrame(right_panel, text="Analysis Options")
        analysis_frame.pack(fill='x', pady=5)
        
        ttk.Button(analysis_frame, text="Monthly Sales Analysis",
                  command=self.analyze_monthly_sales).pack(fill='x', pady=2)
        ttk.Button(analysis_frame, text="Top Products",
                  command=self.analyze_top_products).pack(fill='x', pady=2)
        ttk.Button(analysis_frame, text="Sales Trend",
                  command=self.plot_sales_trend).pack(fill='x', pady=2)
        ttk.Button(analysis_frame, text="Category Distribution",
                  command=self.plot_category_distribution).pack(fill='x', pady=2)
        
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
            
            # Find all tables in the webpage
            tables = pd.read_html(response.text)
            if tables:
                self.df = tables[0]  # Take the first table
                self.data_display.delete(1.0, tk.END)
                self.data_display.insert(tk.END, self.df.to_string())
                
                # Update column selections
                self.x_col['values'] = self.df.columns.tolist()
                self.y_col['values'] = self.df.columns.tolist()
                
                messagebox.showinfo("Success", "Data scraped successfully!")
            else:
                messagebox.showwarning("Warning", "No tables found in the webpage!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape data: {str(e)}")
            
    def analyze_monthly_sales(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data available!")
            return
            
        try:
            # Assuming date column exists
            date_col = next(col for col in self.df.columns if 'date' in col.lower())
            sales_col = next(col for col in self.df.columns if 'sale' in col.lower() or 'amount' in col.lower())
            
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            monthly_sales = self.df.groupby(self.df[date_col].dt.strftime('%Y-%m'))[sales_col].sum()
            
            plt.figure(figsize=(10, 6))
            monthly_sales.plot(kind='bar')
            plt.title('Monthly Sales Analysis')
            plt.xlabel('Month')
            plt.ylabel('Sales')
            plt.xticks(rotation=45)
            
            self.display_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def analyze_top_products(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data available!")
            return
            
        try:
            product_col = next(col for col in self.df.columns if 'product' in col.lower())
            sales_col = next(col for col in self.df.columns if 'sale' in col.lower() or 'amount' in col.lower())
            
            top_products = self.df.groupby(product_col)[sales_col].sum().sort_values(ascending=False).head(10)
            
            plt.figure(figsize=(10, 6))
            top_products.plot(kind='bar')
            plt.title('Top 10 Products by Sales')
            plt.xlabel('Product')
            plt.ylabel('Sales')
            plt.xticks(rotation=45)
            
            self.display_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def plot_sales_trend(self):
        if self.df is None or not (self.x_col.get() and self.y_col.get()):
            messagebox.showwarning("Warning", "Please select columns for analysis!")
            return
            
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(self.df[self.x_col.get()], self.df[self.y_col.get()])
            plt.title('Sales Trend Analysis')
            plt.xlabel(self.x_col.get())
            plt.ylabel(self.y_col.get())
            plt.xticks(rotation=45)
            
            self.display_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot trend: {str(e)}")
            
    def plot_category_distribution(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data available!")
            return
            
        try:
            category_col = next(col for col in self.df.columns if 'category' in col.lower())
            
            plt.figure(figsize=(10, 6))
            self.df[category_col].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Category Distribution')
            
            self.display_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def display_plot(self):
        # Clear previous plot
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Display new plot
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = DataScraperAnalyzer()
    app.run()