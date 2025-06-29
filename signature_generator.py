import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import random
import os
from datetime import datetime

class SignatureGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Signature Generator")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.current_signature = None
        self.signatures = []
        self.fonts = [
            "arial.ttf",
            "times.ttf",
            "calibri.ttf",
            "SCRIPTBL.TTF",  # Script Bold
            "BRUSHSCI.TTF",  # Brush Script
            "FREESCPT.TTF",  # Freestyle Script
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel)
        
        # Input section
        input_frame = ttk.LabelFrame(left_panel, text="Signature Input", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Enter Name/Text:").pack()
        self.text_input = ttk.Entry(input_frame, width=40)
        self.text_input.pack(pady=5)
        
        # Style options
        style_frame = ttk.LabelFrame(left_panel, text="Style Options", padding=10)
        style_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Size selection
        ttk.Label(style_frame, text="Signature Size:").pack()
        self.size_var = tk.IntVar(value=50)
        size_scale = ttk.Scale(style_frame, from_=20, to=100, 
                             variable=self.size_var, orient=tk.HORIZONTAL)
        size_scale.pack(fill=tk.X)
        
        # Color selection
        self.color_var = tk.StringVar(value="black")
        ttk.Button(style_frame, text="Choose Color", 
                  command=self.choose_color).pack(fill=tk.X, pady=5)
        
        # Slant selection
        ttk.Label(style_frame, text="Signature Slant:").pack()
        self.slant_var = tk.IntVar(value=0)
        slant_scale = ttk.Scale(style_frame, from_=-45, to=45, 
                              variable=self.slant_var, orient=tk.HORIZONTAL)
        slant_scale.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Generate Signatures", 
                  command=self.generate_signatures).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Current", 
                  command=self.save_current).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save All", 
                  command=self.save_all).pack(fill=tk.X, pady=2)
        
        # Right panel - Display
        self.display_frame = ttk.Frame(main_container)
        main_container.add(self.display_frame)
        
        # Canvas for signature display
        self.canvas = tk.Canvas(self.display_frame, bg='white', width=800, height=600)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Signature Color")[1]
        if color:
            self.color_var.set(color)
            
    def generate_signatures(self):
        text = self.text_input.get()
        if not text:
            messagebox.showwarning("Warning", "Please enter text first!")
            return
            
        self.signatures = []
        self.canvas.delete("all")
        
        # Generate multiple signatures
        y_offset = 50
        for font_name in self.fonts:
            try:
                # Create image for signature
                img = Image.new('RGBA', (600, 200), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                # Load font
                font_size = self.size_var.get()
                try:
                    font = ImageFont.truetype(font_name, font_size)
                except:
                    font = ImageFont.load_default()
                
                # Draw text
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = (600 - text_width) // 2
                y = (200 - text_height) // 2
                
                draw.text((x, y), text, font=font, fill=self.color_var.get())
                
                # Apply rotation if specified
                if self.slant_var.get() != 0:
                    img = img.rotate(self.slant_var.get(), expand=True)
                
                # Convert to PhotoImage and display
                photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(400, y_offset, image=photo, anchor=tk.CENTER)
                self.canvas.image = photo  # Keep reference
                
                self.signatures.append(img)
                y_offset += 150
                
            except Exception as e:
                print(f"Error with font {font_name}: {str(e)}")
                
        self.current_signature = self.signatures[0] if self.signatures else None
        
    def save_current(self):
        if not self.current_signature:
            messagebox.showwarning("Warning", "Generate signatures first!")
            return
            
        self.save_signature(self.current_signature)
        
    def save_all(self):
        if not self.signatures:
            messagebox.showwarning("Warning", "Generate signatures first!")
            return
            
        for i, sig in enumerate(self.signatures):
            self.save_signature(sig, f"signature_{i+1}_")
            
    def save_signature(self, img, prefix="signature_"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}{timestamp}.png"
        
        try:
            img.save(filename, "PNG")
            messagebox.showinfo("Success", f"Signature saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving signature: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SignatureGenerator(root)
    root.mainloop()