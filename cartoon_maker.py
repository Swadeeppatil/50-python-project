import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os
from datetime import datetime

class CartoonMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartoon Maker")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.characters = {
            "Boy": "assets/boy.png",
            "Girl": "assets/girl.png",
            "Robot": "assets/robot.png",
            "Alien": "assets/alien.png"
        }
        
        self.backgrounds = {
            "Classroom": "assets/classroom.png",
            "Forest": "assets/forest.png",
            "Street": "assets/street.png",
            "Office": "assets/office.png"
        }
        
        self.expressions = ["Happy", "Sad", "Angry", "Surprised"]
        self.poses = ["Standing", "Sitting", "Pointing"]
        self.bubble_types = ["Speech", "Thought", "Shout"]
        
        self.current_scene = {
            "background": None,
            "characters": []
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel)
        
        # Character controls
        char_frame = ttk.LabelFrame(left_panel, text="Character", padding=5)
        char_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(char_frame, text="Select Character:").pack()
        self.char_var = tk.StringVar()
        char_combo = ttk.Combobox(char_frame, textvariable=self.char_var, 
                                 values=list(self.characters.keys()))
        char_combo.pack(fill=tk.X)
        
        # Expression
        ttk.Label(char_frame, text="Expression:").pack()
        self.expr_var = tk.StringVar()
        expr_combo = ttk.Combobox(char_frame, textvariable=self.expr_var, 
                                 values=self.expressions)
        expr_combo.pack(fill=tk.X)
        
        # Pose
        ttk.Label(char_frame, text="Pose:").pack()
        self.pose_var = tk.StringVar()
        pose_combo = ttk.Combobox(char_frame, textvariable=self.pose_var, 
                                 values=self.poses)
        pose_combo.pack(fill=tk.X)
        
        # Color picker
        ttk.Button(char_frame, text="Choose Color", 
                  command=self.choose_color).pack(fill=tk.X, pady=5)
        
        # Add character button
        ttk.Button(char_frame, text="Add Character", 
                  command=self.add_character).pack(fill=tk.X, pady=5)
        
        # Background controls
        bg_frame = ttk.LabelFrame(left_panel, text="Background", padding=5)
        bg_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(bg_frame, text="Select Background:").pack()
        self.bg_var = tk.StringVar()
        bg_combo = ttk.Combobox(bg_frame, textvariable=self.bg_var, 
                               values=list(self.backgrounds.keys()))
        bg_combo.pack(fill=tk.X)
        
        # Dialogue controls
        dialogue_frame = ttk.LabelFrame(left_panel, text="Dialogue", padding=5)
        dialogue_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dialogue_frame, text="Bubble Type:").pack()
        self.bubble_var = tk.StringVar()
        bubble_combo = ttk.Combobox(dialogue_frame, textvariable=self.bubble_var, 
                                   values=self.bubble_types)
        bubble_combo.pack(fill=tk.X)
        
        ttk.Label(dialogue_frame, text="Dialogue Text:").pack()
        self.dialogue_text = tk.Text(dialogue_frame, height=3)
        self.dialogue_text.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Generate Scene", 
                  command=self.generate_scene).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Scene", 
                  command=self.save_scene).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Clear Scene", 
                  command=self.clear_scene).pack(fill=tk.X, pady=2)
        
        # Right panel - Canvas
        self.canvas_frame = ttk.Frame(main_container)
        main_container.add(self.canvas_frame)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', width=800, height=600)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Character Color")[1]
        if color:
            self.current_color = color
            
    def add_character(self):
        char_data = {
            "type": self.char_var.get(),
            "expression": self.expr_var.get(),
            "pose": self.pose_var.get(),
            "color": getattr(self, 'current_color', '#FFFFFF'),
            "position": (100, 100),  # Default position
            "dialogue": {
                "text": self.dialogue_text.get("1.0", tk.END).strip(),
                "type": self.bubble_var.get()
            }
        }
        self.current_scene["characters"].append(char_data)
        self.update_canvas()
        
    def generate_scene(self):
        # Create a new image
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Add background if selected
        if self.bg_var.get():
            # In real implementation, load and paste background image
            draw.rectangle([0, 0, 800, 600], fill='lightblue')
        
        # Add characters and dialogues
        for char in self.current_scene["characters"]:
            # In real implementation, load and paste character image
            x, y = char["position"]
            draw.rectangle([x, y, x+50, y+100], fill=char["color"])
            
            # Add dialogue bubble
            if char["dialogue"]["text"]:
                draw.text((x, y-30), char["dialogue"]["text"], fill='black')
        
        # Convert to PhotoImage and display
        self.scene_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.scene_image, anchor=tk.NW)
        
    def save_scene(self):
        filename = f"cartoon_scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        # In real implementation, save the actual image
        self.canvas.postscript(file=filename)
        
    def clear_scene(self):
        self.current_scene = {"background": None, "characters": []}
        self.canvas.delete("all")
        
    def update_canvas(self):
        self.generate_scene()

if __name__ == "__main__":
    root = tk.Tk()
    app = CartoonMaker(root)
    root.mainloop()