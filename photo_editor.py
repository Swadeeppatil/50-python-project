import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import mediapipe as mp
from rembg import remove
import os
from datetime import datetime

class PhotoEditor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Advanced Photo Editor")
        self.window.geometry("1400x800")
        self.window.configure(bg='#2C3E50')
        
        self.original_image = None
        self.edited_image = None
        self.current_tool = None
        self.selected_part = None
        self.undo_stack = []
        
        self.mp_pose = mp.solutions.pose.Pose()
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
        
        self.create_gui()
        
    def create_gui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Tools Panel
        tools_panel = ttk.LabelFrame(main_frame, text="Editing Tools")
        tools_panel.pack(side='left', fill='y', padx=5)
        
        tools = [
            ("Load Image", self.load_image),
            ("Select Body Part", lambda: self.set_tool("body")),
            ("Change Color", lambda: self.set_tool("color")),
            ("Move Part", lambda: self.set_tool("move")),
            ("Remove Background", self.remove_background),
            ("Undo", self.undo),
            ("Save Image", self.save_image)
        ]
        
        for text, command in tools:
            ttk.Button(tools_panel, text=text, command=command).pack(fill='x', pady=2)
        
        # Center Image Panel
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.canvas = tk.Canvas(self.image_frame, bg='white')
        self.canvas.pack(fill='both', expand=True)
        
        # Mouse bindings
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        
        # Right Control Panel
        control_panel = ttk.LabelFrame(main_frame, text="Controls")
        control_panel.pack(side='right', fill='y', padx=5)
        
        # Color controls
        color_frame = ttk.LabelFrame(control_panel, text="Color Adjustment")
        color_frame.pack(fill='x', pady=5)
        
        self.create_slider(color_frame, "Hue", 0, 179)
        self.create_slider(color_frame, "Saturation", 0, 255)
        self.create_slider(color_frame, "Value", 0, 255)
        
        # Part selection
        self.part_var = tk.StringVar(value="upper_body")
        parts_frame = ttk.LabelFrame(control_panel, text="Body Parts")
        parts_frame.pack(fill='x', pady=5)
        
        parts = ["face", "upper_body", "lower_body", "arms", "legs"]
        for part in parts:
            ttk.Radiobutton(parts_frame, text=part.replace("_", " ").title(),
                          variable=self.part_var, value=part).pack(anchor='w')
    
    def create_slider(self, parent, name, from_, to):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=name).pack(side='left')
        slider = ttk.Scale(frame, from_=from_, to=to, orient='horizontal')
        slider.pack(side='right', fill='x', expand=True)
        setattr(self, f"{name.lower()}_slider", slider)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        
        if file_path:
            try:
                self.original_image = cv2.imread(file_path)
                self.edited_image = self.original_image.copy()
                self.undo_stack = [self.original_image.copy()]
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def display_image(self):
        if self.edited_image is not None:
            image_rgb = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB)
            height, width = image_rgb.shape[:2]
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            scale = min(canvas_width/width, canvas_height/height)
            
            if scale < 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
            
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(image_rgb))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
    
    def set_tool(self, tool):
        self.current_tool = tool
        if tool == "body":
            self.detect_body_parts()
    
    def detect_body_parts(self):
        if self.edited_image is None:
            return
            
        with self.mp_pose.process(cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB)) as results:
            if results.pose_landmarks:
                self.draw_body_landmarks(results.pose_landmarks)
    
    def draw_body_landmarks(self, landmarks):
        temp_image = self.edited_image.copy()
        h, w = temp_image.shape[:2]
        
        for landmark in landmarks.landmark:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(temp_image, (x, y), 5, (0, 255, 0), -1)
        
        self.edited_image = temp_image
        self.display_image()
    
    def start_selection(self, event):
        if self.current_tool in ["color", "move"]:
            self.selected_part = []
            self.selected_part.append((event.x, event.y))
    
    def update_selection(self, event):
        if self.current_tool in ["color", "move"] and self.selected_part:
            self.selected_part.append((event.x, event.y))
            self.draw_selection()
    
    def draw_selection(self):
        if self.selected_part:
            temp_image = self.edited_image.copy()
            points = np.array(self.selected_part, np.int32)
            cv2.polylines(temp_image, [points], True, (0, 255, 0), 2)
            self.display_image()
    
    def end_selection(self, event):
        if self.current_tool == "color" and self.selected_part:
            self.apply_color_change()
        elif self.current_tool == "move" and self.selected_part:
            self.move_selected_part()
    
    def apply_color_change(self):
        if not self.selected_part:
            return
            
        mask = np.zeros(self.edited_image.shape[:2], dtype=np.uint8)
        points = np.array(self.selected_part, np.int32)
        cv2.fillPoly(mask, [points], 255)
        
        hsv = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2HSV)
        hsv[mask == 255, 0] = self.hue_slider.get()
        hsv[mask == 255, 1] = self.saturation_slider.get()
        hsv[mask == 255, 2] = self.value_slider.get()
        
        self.undo_stack.append(self.edited_image.copy())
        self.edited_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        self.display_image()
    
    def move_selected_part(self):
        if not self.selected_part:
            return
            
        # Create mask for selected region
        mask = np.zeros(self.edited_image.shape[:2], dtype=np.uint8)
        points = np.array(self.selected_part, np.int32)
        cv2.fillPoly(mask, [points], 255)
        
        # Copy selected region
        selected_region = cv2.bitwise_and(self.edited_image, self.edited_image, mask=mask)
        
        # Move region (simple implementation - can be enhanced)
        M = np.float32([[1, 0, 50], [0, 1, 50]])
        moved_region = cv2.warpAffine(selected_region, M, 
                                    (self.edited_image.shape[1], self.edited_image.shape[0]))
        
        # Combine images
        self.undo_stack.append(self.edited_image.copy())
        self.edited_image = cv2.add(self.edited_image, moved_region)
        self.display_image()
    
    def remove_background(self):
        if self.edited_image is None:
            return
            
        try:
            rgb_image = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB)
            self.undo_stack.append(self.edited_image.copy())
            no_bg = remove(rgb_image)
            self.edited_image = cv2.cvtColor(np.array(no_bg), cv2.COLOR_RGB2BGR)
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Background removal failed: {str(e)}")
    
    def undo(self):
        if len(self.undo_stack) > 0:
            self.edited_image = self.undo_stack.pop()
            self.display_image()
    
    def save_image(self):
        if self.edited_image is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            
        if file_path:
            try:
                cv2.imwrite(file_path, self.edited_image)
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PhotoEditor()
    app.run()