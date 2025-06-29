import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import cv2
import numpy as np
import dlib
import face_recognition
from datetime import datetime
import os

class AgeProgressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Age Progression Generator")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.original_image = None
        self.current_image = None
        self.face_detector = dlib.get_frontal_face_detector()
        self.age_options = [30, 40, 50, 60, 70]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel)
        
        # Upload section
        upload_frame = ttk.LabelFrame(left_panel, text="Upload Photo", padding=5)
        upload_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(upload_frame, text="Upload Photo", 
                  command=self.upload_photo).pack(fill=tk.X, pady=5)
        
        # Age selection
        age_frame = ttk.LabelFrame(left_panel, text="Age Selection", padding=5)
        age_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(age_frame, text="Select Target Age:").pack()
        self.age_var = tk.IntVar(value=30)
        for age in self.age_options:
            ttk.Radiobutton(age_frame, text=f"{age} years", 
                          variable=self.age_var, value=age).pack()
        
        # Features frame
        features_frame = ttk.LabelFrame(left_panel, text="Aging Features", padding=5)
        features_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Wrinkles
        ttk.Label(features_frame, text="Wrinkle Intensity:").pack()
        self.wrinkle_var = tk.DoubleVar(value=0.5)
        ttk.Scale(features_frame, from_=0, to=1, variable=self.wrinkle_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Gray Hair
        ttk.Label(features_frame, text="Gray Hair Amount:").pack()
        self.gray_var = tk.DoubleVar(value=0.5)
        ttk.Scale(features_frame, from_=0, to=1, variable=self.gray_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Generate Aged Photo", 
                  command=self.generate_aged_photo).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Result", 
                  command=self.save_result).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Reset", 
                  command=self.reset).pack(fill=tk.X, pady=2)
        
        # Right panel - Image display
        self.display_frame = ttk.Frame(main_container)
        main_container.add(self.display_frame)
        
        # Original photo
        self.original_label = ttk.Label(self.display_frame, text="Original Photo")
        self.original_label.pack(pady=5)
        self.original_canvas = tk.Canvas(self.display_frame, width=400, height=300)
        self.original_canvas.pack(pady=5)
        
        # Aged photo
        self.aged_label = ttk.Label(self.display_frame, text="Aged Photo")
        self.aged_label.pack(pady=5)
        self.aged_canvas = tk.Canvas(self.display_frame, width=400, height=300)
        self.aged_canvas.pack(pady=5)
        
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                # Resize image to fit canvas
                self.original_image.thumbnail((400, 300))
                self.display_original_image()
                messagebox.showinfo("Success", "Photo uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error uploading photo: {str(e)}")
    
    def display_original_image(self):
        if self.original_image:
            photo = ImageTk.PhotoImage(self.original_image)
            self.original_canvas.create_image(
                200, 150, image=photo, anchor=tk.CENTER
            )
            self.original_canvas.image = photo
    
    def generate_aged_photo(self):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please upload a photo first!")
            return
        
        try:
            # Convert PIL Image to numpy array
            img_array = np.array(self.original_image)
            
            # Detect face
            face_locations = face_recognition.face_locations(img_array)
            if not face_locations:
                messagebox.showerror("Error", "No face detected in the photo!")
                return
            
            # Apply aging effects
            aged_image = self.apply_aging_effects(img_array)
            
            # Display result
            self.current_image = Image.fromarray(aged_image)
            photo = ImageTk.PhotoImage(self.current_image)
            self.aged_canvas.create_image(200, 150, image=photo, anchor=tk.CENTER)
            self.aged_canvas.image = photo
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating aged photo: {str(e)}")
    
    def apply_aging_effects(self, image):
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply wrinkles based on intensity
        wrinkle_intensity = self.wrinkle_var.get()
        aged = cv2.GaussianBlur(gray, (5, 5), 2)
        aged = cv2.addWeighted(gray, 1 + wrinkle_intensity, aged, -wrinkle_intensity, 0)
        
        # Apply gray hair effect
        gray_amount = self.gray_var.get()
        colored = image.copy()
        gray_image = cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), 
                                cv2.COLOR_GRAY2RGB)
        aged_color = cv2.addWeighted(colored, 1 - gray_amount, gray_image, 
                                   gray_amount, 0)
        
        # Enhance aging features based on selected age
        age_factor = (self.age_var.get() - 30) / 40  # Normalize to 0-1
        aged_enhanced = cv2.addWeighted(aged_color, 1 + age_factor, 
                                      aged_color, -age_factor, 0)
        
        return aged_enhanced
    
    def save_result(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Generate an aged photo first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"aged_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving image: {str(e)}")
    
    def reset(self):
        self.original_canvas.delete("all")
        self.aged_canvas.delete("all")
        self.original_image = None
        self.current_image = None
        self.wrinkle_var.set(0.5)
        self.gray_var.set(0.5)
        self.age_var.set(30)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgeProgressionApp(root)
    root.mainloop()