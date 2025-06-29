import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from urllib.parse import urlparse
import os

class WebScraper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Web Scraper")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2C3E50')
        
        # Data variables
        self.scraped_data = None
        self.current_url = ""
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # URL input
        url_frame = ttk.LabelFrame(main_frame, text="Website URL")
        url_frame.pack(fill='x', pady=5)
        
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.pack(side='left', padx=5, pady=5, expand=True)
        
        ttk.Button(url_frame, text="Scrape",
                  command=self.scrape_website).pack(side='right', padx=5)
        
        # Elements selection
        elements_frame = ttk.LabelFrame(main_frame, text="Elements to Extract")
        elements_frame.pack(fill='x', pady=5)
        
        self.elements_var = tk.StringVar(value='text')
        elements = [
            ('Text Content', 'text'),
            ('Links', 'links'),
            ('Images', 'images'),
            ('Tables', 'tables'),
            ('Custom Tags', 'custom')
        ]
        
        for text, value in elements:
            ttk.Radiobutton(elements_frame, text=text,
                          variable=self.elements_var,
                          value=value).pack(side='left', padx=10)
        
        # Custom tag input
        self.custom_tag = ttk.Entry(elements_frame, width=20)
        self.custom_tag.pack(side='left', padx=5)
        ttk.Label(elements_frame, text="Custom Tag").pack(side='left')
        
        # Data display
        display_frame = ttk.LabelFrame(main_frame, text="Scraped Data")
        display_frame.pack(fill='both', expand=True, pady=5)
        
        self.data_display = scrolledtext.ScrolledText(display_frame,
                                                    wrap=tk.WORD,
                                                    width=80,
                                                    height=20)
        self.data_display.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Data operations
        operations_frame = ttk.LabelFrame(main_frame, text="Data Operations")
        operations_frame.pack(fill='x', pady=5)
        
        ttk.Button(operations_frame, text="Clean Data",
                  command=self.clean_data).pack(side='left', padx=5)
        ttk.Button(operations_frame, text="Extract Emails",
                  command=self.extract_emails).pack(side='left', padx=5)
        ttk.Button(operations_frame, text="Extract Phone Numbers",
                  command=self.extract_phone_numbers).pack(side='left', padx=5)
        ttk.Button(operations_frame, text="Count Words",
                  command=self.count_words).pack(side='left', padx=5)
        ttk.Button(operations_frame, text="Save as CSV",
                  command=lambda: self.save_data('csv')).pack(side='left', padx=5)
        ttk.Button(operations_frame, text="Save as JSON",
                  command=lambda: self.save_data('json')).pack(side='left', padx=5)
        
    def scrape_website(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL!")
            return
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            element_type = self.elements_var.get()
            
            if element_type == 'text':
                self.scraped_data = soup.get_text()
            elif element_type == 'links':
                self.scraped_data = [link.get('href') for link in soup.find_all('a')]
            elif element_type == 'images':
                self.scraped_data = [img.get('src') for img in soup.find_all('img')]
            elif element_type == 'tables':
                tables = []
                for table in soup.find_all('table'):
                    df = pd.read_html(str(table))[0]
                    tables.append(df.to_string())
                self.scraped_data = '\n\n'.join(tables)
            elif element_type == 'custom':
                tag = self.custom_tag.get()
                if tag:
                    self.scraped_data = [elem.get_text() for elem in soup.find_all(tag)]
                else:
                    messagebox.showwarning("Warning", "Please enter a custom tag!")
                    return
            
            self.display_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape website: {str(e)}")
            
    def display_data(self):
        self.data_display.delete(1.0, tk.END)
        if isinstance(self.scraped_data, list):
            self.data_display.insert(tk.END, '\n'.join(map(str, self.scraped_data)))
        else:
            self.data_display.insert(tk.END, str(self.scraped_data))
            
    def clean_data(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to clean!")
            return
            
        if isinstance(self.scraped_data, str):
            # Remove extra whitespace and special characters
            cleaned = re.sub(r'\s+', ' ', self.scraped_data)
            cleaned = re.sub(r'[^\w\s@.-]', '', cleaned)
            self.scraped_data = cleaned.strip()
        elif isinstance(self.scraped_data, list):
            # Clean each item in the list
            self.scraped_data = [re.sub(r'\s+', ' ', str(item)).strip() 
                               for item in self.scraped_data]
            
        self.display_data()
        
    def extract_emails(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to process!")
            return
            
        text = str(self.scraped_data)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        self.scraped_data = emails
        self.display_data()
        
    def extract_phone_numbers(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to process!")
            return
            
        text = str(self.scraped_data)
        phones = re.findall(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
        self.scraped_data = phones
        self.display_data()
        
    def count_words(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to process!")
            return
            
        text = str(self.scraped_data)
        words = text.split()
        word_count = {}
        
        for word in words:
            word = word.lower()
            if word.isalnum():
                word_count[word] = word_count.get(word, 0) + 1
                
        # Sort by frequency
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        self.scraped_data = [f"{word}: {count}" for word, count in sorted_words]
        self.display_data()
        
    def save_data(self, format_type):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to save!")
            return
            
        file_types = {
            'csv': [('CSV files', '*.csv')],
            'json': [('JSON files', '*.json')]
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=file_types[format_type])
            
        if file_path:
            try:
                if format_type == 'csv':
                    if isinstance(self.scraped_data, list):
                        df = pd.DataFrame(self.scraped_data, columns=['Data'])
                    else:
                        df = pd.DataFrame([self.scraped_data], columns=['Data'])
                    df.to_csv(file_path, index=False)
                else:  # JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.scraped_data, f, indent=4)
                        
                messagebox.showinfo("Success", "Data saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WebScraper()
    app.run()