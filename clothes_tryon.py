import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from datetime import datetime

class ClothesVirtualTryOn:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Virtual Clothes Try-On")
        self.window.geometry("1400x800")
        self.window.configure(bg='#E8F6F3')
        
        # Initialize variables
        self.person_image = None
        self.clothes_image = None
        self.result_image = None
        self.person_photo = None
        self.clothes_photo = None
        self.result_photo = None
        self.clothes_position = [0, 0]
        self.clothes_scale = 1.0
        self.clothes_rotation = 0
        self.clothes_library = {}
        self.alpha_value = 0.8
        self.canvas_size = (500, 600)
        
        self.create_gui()
        self.load_clothes_library()
        
    def create_gui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Panel - Person Image
        left_panel = ttk.LabelFrame(main_frame, text="Person Image")
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        self.person_canvas = tk.Canvas(left_panel, bg='white')
        self.person_canvas.pack(fill='both', expand=True, pady=5)
        
        ttk.Button(left_panel, text="Load Person Image",
                  command=self.load_person_image).pack(fill='x', pady=2)
        
        # Center Panel - Clothes and Controls
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        # Clothes Library
        library_frame = ttk.LabelFrame(center_panel, text="Clothes Library")
        library_frame.pack(fill='x', pady=5)
        
        self.clothes_listbox = tk.Listbox(library_frame, height=6)
        self.clothes_listbox.pack(fill='x', pady=5)
        self.clothes_listbox.bind('<<ListboxSelect>>', self.select_clothes)
        
        ttk.Button(library_frame, text="Add New Clothes",
                  command=self.add_clothes).pack(fill='x', pady=2)
        
        # Adjustment Controls
        controls_frame = ttk.LabelFrame(center_panel, text="Adjustments")
        controls_frame.pack(fill='x', pady=5)
        
        # Position controls
        ttk.Label(controls_frame, text="Position:").pack(anchor='w')
        position_frame = ttk.Frame(controls_frame)
        position_frame.pack(fill='x', pady=2)
        
        ttk.Label(position_frame, text="X:").pack(side='left')
        self.x_scale = ttk.Scale(position_frame, from_=-200, to=200,
                                orient='horizontal', command=self.update_position)
        self.x_scale.pack(side='left', fill='x', expand=True)
        
        ttk.Label(position_frame, text="Y:").pack(side='left')
        self.y_scale = ttk.Scale(position_frame, from_=-200, to=200,
                                orient='horizontal', command=self.update_position)
        self.y_scale.pack(side='left', fill='x', expand=True)
        
        # Scale control
        ttk.Label(controls_frame, text="Size:").pack(anchor='w')
        self.scale_slider = ttk.Scale(controls_frame, from_=0.5, to=2.0,
                                    orient='horizontal', command=self.update_scale)
        self.scale_slider.set(1.0)
        self.scale_slider.pack(fill='x', pady=2)
        
        # Rotation control
        ttk.Label(controls_frame, text="Rotation:").pack(anchor='w')
        self.rotation_slider = ttk.Scale(controls_frame, from_=0, to=360,
                                       orient='horizontal', command=self.update_rotation)
        self.rotation_slider.pack(fill='x', pady=2)
        
        # Right Panel - Result
        right_panel = ttk.LabelFrame(main_frame, text="Result")
        right_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        self.result_canvas = tk.Canvas(right_panel, bg='white')
        self.result_canvas.pack(fill='both', expand=True, pady=5)
        
        ttk.Button(right_panel, text="Save Result",
                  command=self.save_result).pack(fill='x', pady=2)
        
    def load_person_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        
        if file_path:
            try:
                self.person_image = cv2.imread(file_path)
                self.display_person_image()
                self.update_result()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_person_image(self):
        if self.person_image is not None:
            image_rgb = cv2.cvtColor(self.person_image, cv2.COLOR_BGR2RGB)
            height, width = image_rgb.shape[:2]
            
            # Resize to fit canvas
            canvas_width = self.person_canvas.winfo_width()
            canvas_height = self.person_canvas.winfo_height()
            scale = min(canvas_width/width, canvas_height/height)
            
            if scale < 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
            
            self.person_photo = ImageTk.PhotoImage(image=Image.fromarray(image_rgb))
            self.person_canvas.delete("all")
            self.person_canvas.create_image(0, 0, anchor='nw', image=self.person_photo)
            
    def add_clothes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png")])
        
        if file_path:
            try:
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.clothes_library[name] = file_path
                self.clothes_listbox.insert(tk.END, name)
                self.save_clothes_library()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add clothes: {str(e)}")
                
    def select_clothes(self, event):
        selection = self.clothes_listbox.curselection()
        if selection:
            name = self.clothes_listbox.get(selection[0])
            try:
                self.clothes_image = cv2.imread(self.clothes_library[name], -1)
                self.update_result()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load clothes: {str(e)}")
                
    def update_position(self, _=None):
        self.clothes_position = [self.x_scale.get(), self.y_scale.get()]
        self.update_result()
        
    def update_scale(self, _=None):
        self.clothes_scale = self.scale_slider.get()
        self.update_result()
        
    def update_rotation(self, _=None):
        self.clothes_rotation = self.rotation_slider.get()
        self.update_result()
        
    def update_result(self):
        if self.person_image is None or self.clothes_image is None:
            return
            
        try:
            # Create result image
            result = self.person_image.copy()
            
            # Process clothes image
            clothes = self.clothes_image.copy()
            
            # Scale
            if self.clothes_scale != 1.0:
                h, w = clothes.shape[:2]
                new_h, new_w = int(h * self.clothes_scale), int(w * self.clothes_scale)
                clothes = cv2.resize(clothes, (new_w, new_h))
            
            # Rotate
            if self.clothes_rotation != 0:
                h, w = clothes.shape[:2]
                M = cv2.getRotationMatrix2D((w/2, h/2), self.clothes_rotation, 1)
                clothes = cv2.warpAffine(clothes, M, (w, h))
            
            # Calculate position
            y_offset = int(result.shape[0]/2 + self.clothes_position[1])
            x_offset = int(result.shape[1]/2 + self.clothes_position[0])
            
            # Blend images
            if clothes.shape[2] == 4:  # With alpha channel
                alpha = clothes[:, :, 3] / 255.0
                for c in range(3):
                    result[y_offset:y_offset+clothes.shape[0],
                          x_offset:x_offset+clothes.shape[1], c] = \
                        (1-alpha) * result[y_offset:y_offset+clothes.shape[0],
                                         x_offset:x_offset+clothes.shape[1], c] + \
                        alpha * clothes[:, :, c]
            
            # Display result
            image_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            self.result_photo = ImageTk.PhotoImage(image=Image.fromarray(image_rgb))
            self.result_canvas.delete("all")
            self.result_canvas.create_image(0, 0, anchor='nw', image=self.result_photo)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update result: {str(e)}")
            
    def save_result(self):
        if self.result_photo is None:
            messagebox.showwarning("Warning", "No result to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            
        if file_path:
            try:
                cv2.imwrite(file_path, cv2.cvtColor(
                    np.array(self.result_photo), cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Success", "Result saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save result: {str(e)}")
                
    def load_clothes_library(self):
        try:
            if os.path.exists('clothes_library.txt'):
                with open('clothes_library.txt', 'r') as f:
                    self.clothes_library = {line.split('|')[0]: line.split('|')[1].strip()
                                          for line in f.readlines()}
                    for name in self.clothes_library:
                        self.clothes_listbox.insert(tk.END, name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load clothes library: {str(e)}")
            
    def save_clothes_library(self):
        try:
            with open('clothes_library.txt', 'w') as f:
                for name, path in self.clothes_library.items():
                    f.write(f"{name}|{path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save clothes library: {str(e)}")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ClothesVirtualTryOn()
    app.run()