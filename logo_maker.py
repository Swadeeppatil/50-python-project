import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import os

class LogoMaker:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Logo Maker")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2C3E50')
        
        # Logo variables
        self.logo_image = None
        self.current_display = None
        self.company_name = ""
        self.font_size = 72
        self.font_color = "#FFFFFF"
        self.bg_color = "#2C3E50"
        self.logo_shape = "circle"
        self.current_font = "arial.ttf"
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Logo display
        left_panel = ttk.LabelFrame(main_frame, text="Logo Preview")
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        self.canvas = tk.Canvas(left_panel, bg='#34495E', width=600, height=600)
        self.canvas.pack(expand=True, fill='both', pady=5)
        
        # Right panel - Controls
        right_panel = ttk.LabelFrame(main_frame, text="Logo Controls")
        right_panel.pack(side='right', fill='y', padx=5)
        
        # Company name input
        ttk.Label(right_panel, text="Company Name:").pack(anchor='w', pady=5)
        self.name_entry = ttk.Entry(right_panel, width=30)
        self.name_entry.pack(fill='x', pady=5)
        
        # Font size control
        ttk.Label(right_panel, text="Font Size:").pack(anchor='w', pady=5)
        self.size_scale = ttk.Scale(right_panel, from_=20, to=150,
                                  orient='horizontal',
                                  command=self.update_font_size)
        self.size_scale.set(72)
        self.size_scale.pack(fill='x', pady=5)
        
        # Color controls
        colors_frame = ttk.LabelFrame(right_panel, text="Colors")
        colors_frame.pack(fill='x', pady=5)
        
        ttk.Button(colors_frame, text="Choose Font Color",
                  command=self.choose_font_color).pack(fill='x', pady=2)
        ttk.Button(colors_frame, text="Choose Background Color",
                  command=self.choose_bg_color).pack(fill='x', pady=2)
        
        # Shape selection
        shapes_frame = ttk.LabelFrame(right_panel, text="Logo Shape")
        shapes_frame.pack(fill='x', pady=5)
        
        shapes = ['circle', 'square', 'triangle', 'none']
        self.shape_var = tk.StringVar(value='circle')
        for shape in shapes:
            ttk.Radiobutton(shapes_frame, text=shape.capitalize(),
                          variable=self.shape_var,
                          value=shape,
                          command=self.update_logo).pack(fill='x', pady=2)
        
        # Font selection
        fonts_frame = ttk.LabelFrame(right_panel, text="Font Style")
        fonts_frame.pack(fill='x', pady=5)
        
        fonts = ['arial.ttf', 'times.ttf', 'verdana.ttf', 'impact.ttf']
        self.font_var = tk.StringVar(value='arial.ttf')
        for font in fonts:
            ttk.Radiobutton(fonts_frame, text=font.split('.')[0].capitalize(),
                          variable=self.font_var,
                          value=font,
                          command=self.update_logo).pack(fill='x', pady=2)
        
        # Action buttons
        ttk.Button(right_panel, text="Generate Logo",
                  command=self.generate_logo).pack(fill='x', pady=10)
        ttk.Button(right_panel, text="Save Logo",
                  command=self.save_logo).pack(fill='x', pady=2)
        ttk.Button(right_panel, text="Random Style",
                  command=self.random_style).pack(fill='x', pady=2)
        
    def generate_logo(self):
        self.company_name = self.name_entry.get()
        if not self.company_name:
            messagebox.showwarning("Warning", "Please enter a company name!")
            return
            
        # Create base image
        img_size = (600, 600)
        self.logo_image = Image.new('RGB', img_size, self.bg_color)
        draw = ImageDraw.Draw(self.logo_image)
        
        try:
            font = ImageFont.truetype(self.font_var.get(), self.font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), self.company_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (img_size[0] - text_width) // 2
        y = (img_size[1] - text_height) // 2
        
        # Draw shape
        if self.shape_var.get() != 'none':
            if self.shape_var.get() == 'circle':
                draw.ellipse([50, 50, 550, 550], outline=self.font_color, width=5)
            elif self.shape_var.get() == 'square':
                draw.rectangle([50, 50, 550, 550], outline=self.font_color, width=5)
            elif self.shape_var.get() == 'triangle':
                draw.polygon([(300, 50), (50, 550), (550, 550)],
                           outline=self.font_color, width=5)
        
        # Draw text
        draw.text((x, y), self.company_name, font=font, fill=self.font_color)
        
        self.display_logo()
        
    def display_logo(self):
        if self.logo_image:
            self.current_display = ImageTk.PhotoImage(self.logo_image)
            self.canvas.delete('all')
            self.canvas.create_image(300, 300, image=self.current_display)
            
    def choose_font_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")[1]
        if color:
            self.font_color = color
            self.update_logo()
            
    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.update_logo()
            
    def update_font_size(self, value):
        self.font_size = int(float(value))
        self.update_logo()
        
    def update_logo(self):
        if self.company_name:
            self.generate_logo()
            
    def random_style(self):
        # Generate random colors
        self.font_color = f"#{random.randint(0, 0xFFFFFF):06x}"
        self.bg_color = f"#{random.randint(0, 0xFFFFFF):06x}"
        
        # Random font size
        self.font_size = random.randint(40, 120)
        self.size_scale.set(self.font_size)
        
        # Random shape
        shapes = ['circle', 'square', 'triangle', 'none']
        self.shape_var.set(random.choice(shapes))
        
        # Random font
        fonts = ['arial.ttf', 'times.ttf', 'verdana.ttf', 'impact.ttf']
        self.font_var.set(random.choice(fonts))
        
        self.update_logo()
        
    def save_logo(self):
        if self.logo_image is None:
            messagebox.showwarning("Warning", "Generate a logo first!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"),
                      ("JPEG files", "*.jpg"),
                      ("All files", "*.*")])
        
        if file_path:
            self.logo_image.save(file_path)
            messagebox.showinfo("Success", "Logo saved successfully!")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LogoMaker()
    app.run()