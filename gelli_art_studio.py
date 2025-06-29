import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import cv2
import random
import os

class GelliArtStudio:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Gelli Art Studio")
        self.window.geometry("1400x800")
        self.window.configure(bg='#2C3E50')
        
        # Image variables
        self.original_image = None
        self.current_image = None
        self.gelli_image = None
        
        # Effect parameters
        self.texture_strength = 0.5
        self.color_balance = {'R': 1.0, 'G': 1.0, 'B': 1.0}
        self.pattern_size = 50
        self.overlay_opacity = 0.7
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Image display
        left_panel = ttk.LabelFrame(main_frame, text="Canvas")
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        self.canvas = tk.Canvas(left_panel, bg='#34495E', width=800, height=600)
        self.canvas.pack(expand=True, fill='both', pady=5)
        
        # Right panel - Controls
        right_panel = ttk.LabelFrame(main_frame, text="Controls")
        right_panel.pack(side='right', fill='y', padx=5)
        
        # Image controls
        ttk.Button(right_panel, text="Load Image",
                  command=self.load_image).pack(fill='x', pady=2)
        ttk.Button(right_panel, text="Apply Gelli Effect",
                  command=self.apply_gelli_effect).pack(fill='x', pady=2)
        ttk.Button(right_panel, text="Save Result",
                  command=self.save_image).pack(fill='x', pady=2)
        
        # Effect controls
        effects_frame = ttk.LabelFrame(right_panel, text="Effect Settings")
        effects_frame.pack(fill='x', pady=5)
        
        # Texture strength
        ttk.Label(effects_frame, text="Texture Strength:").pack(anchor='w')
        self.texture_scale = ttk.Scale(effects_frame, from_=0, to=1,
                                     orient='horizontal',
                                     command=self.update_texture)
        self.texture_scale.set(0.5)
        self.texture_scale.pack(fill='x')
        
        # Pattern size
        ttk.Label(effects_frame, text="Pattern Size:").pack(anchor='w')
        self.pattern_scale = ttk.Scale(effects_frame, from_=10, to=100,
                                     orient='horizontal',
                                     command=self.update_pattern)
        self.pattern_scale.set(50)
        self.pattern_scale.pack(fill='x')
        
        # Color controls
        colors_frame = ttk.LabelFrame(right_panel, text="Color Balance")
        colors_frame.pack(fill='x', pady=5)
        
        for color in ['R', 'G', 'B']:
            ttk.Label(colors_frame, text=f"{color}:").pack(anchor='w')
            scale = ttk.Scale(colors_frame, from_=0, to=2,
                            orient='horizontal',
                            command=lambda v, c=color: self.update_color(c, v))
            scale.set(1.0)
            scale.pack(fill='x')
        
        # Style presets
        presets_frame = ttk.LabelFrame(right_panel, text="Style Presets")
        presets_frame.pack(fill='x', pady=5)
        
        styles = ['Vintage', 'Modern', 'Abstract', 'Minimal']
        for style in styles:
            ttk.Button(presets_frame, text=style,
                      command=lambda s=style: self.apply_preset(s)).pack(fill='x', pady=2)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        
        if file_path:
            self.original_image = Image.open(file_path)
            self.resize_image()
            self.display_image(self.current_image)
            
    def resize_image(self):
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_ratio = 800/600
        image_ratio = self.original_image.width/self.original_image.height
        
        if image_ratio > canvas_ratio:
            new_width = 800
            new_height = int(800/image_ratio)
        else:
            new_height = 600
            new_width = int(600*image_ratio)
            
        self.current_image = self.original_image.resize((new_width, new_height),
                                                       Image.LANCZOS)
        
    def display_image(self, image):
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete('all')
        self.canvas.create_image(400, 300, image=self.photo)
        
    def apply_gelli_effect(self):
        if self.current_image is None:
            return
            
        # Convert to numpy array
        img_array = np.array(self.current_image)
        
        # Create texture pattern
        texture = self.create_texture_pattern(img_array.shape)
        
        # Apply color adjustments
        for idx, color in enumerate(['R', 'G', 'B']):
            img_array[:,:,idx] = np.clip(
                img_array[:,:,idx] * self.color_balance[color], 0, 255)
        
        # Blend texture with image
        result = cv2.addWeighted(
            img_array, 1-self.texture_strength,
            texture, self.texture_strength, 0)
        
        # Apply artistic filters
        result = cv2.GaussianBlur(result, (5,5), 0)
        result = cv2.detailEnhance(result, sigma_s=10, sigma_r=0.15)
        
        # Convert back to PIL Image
        self.gelli_image = Image.fromarray(result.astype('uint8'))
        self.display_image(self.gelli_image)
        
    def create_texture_pattern(self, shape):
        texture = np.zeros(shape, dtype=np.uint8)
        
        # Create random patterns
        for _ in range(int(100 * self.texture_strength)):
            x = random.randint(0, shape[1]-1)
            y = random.randint(0, shape[0]-1)
            size = random.randint(10, self.pattern_size)
            color = random.randint(150, 255)
            cv2.circle(texture, (x,y), size, (color,color,color), -1)
            
        # Add noise
        noise = np.random.normal(0, 25, shape).astype(np.uint8)
        texture = cv2.add(texture, noise)
        
        return texture
        
    def update_texture(self, value):
        self.texture_strength = float(value)
        
    def update_pattern(self, value):
        self.pattern_size = int(float(value))
        
    def update_color(self, color, value):
        self.color_balance[color] = float(value)
        
    def apply_preset(self, style):
        presets = {
            'Vintage': {'texture': 0.7, 'pattern': 70,
                       'colors': {'R': 1.2, 'G': 0.9, 'B': 0.8}},
            'Modern': {'texture': 0.3, 'pattern': 30,
                      'colors': {'R': 1.0, 'G': 1.1, 'B': 1.1}},
            'Abstract': {'texture': 0.8, 'pattern': 90,
                        'colors': {'R': 1.3, 'G': 0.7, 'B': 1.2}},
            'Minimal': {'texture': 0.2, 'pattern': 20,
                       'colors': {'R': 1.0, 'G': 1.0, 'B': 1.0}}
        }
        
        preset = presets[style]
        self.texture_strength = preset['texture']
        self.pattern_size = preset['pattern']
        self.color_balance = preset['colors']
        
        self.texture_scale.set(preset['texture'])
        self.pattern_scale.set(preset['pattern'])
        self.apply_gelli_effect()
        
    def save_image(self):
        if self.gelli_image is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"),
                      ("JPEG files", "*.jpg"),
                      ("All files", "*.*")])
        
        if file_path:
            self.gelli_image.save(file_path)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = GelliArtStudio()
    app.run()