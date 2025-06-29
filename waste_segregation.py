import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
from ultralytics import YOLO
import json
import os

class WasteSegregationAssistant:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Smart Waste Segregation Assistant")
        self.root.geometry("1200x800")
        
        # Initialize YOLO model
        self.model = YOLO("yolov8n.pt")
        
        # Initialize database
        self.init_database()
        
        # Waste categories and instructions
        self.waste_categories = {
            "plastic": {"bin": "Recycling Bin", "color": "blue"},
            "paper": {"bin": "Recycling Bin", "color": "blue"},
            "metal": {"bin": "Recycling Bin", "color": "blue"},
            "glass": {"bin": "Recycling Bin", "color": "blue"},
            "organic": {"bin": "Compost Bin", "color": "green"},
            "electronic": {"bin": "E-Waste Bin", "color": "red"},
            "other": {"bin": "General Waste", "color": "gray"}
        }
        
        self.setup_gui()
        self.setup_camera()

    def init_database(self):
        self.conn = sqlite3.connect('waste_data.db')
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS segregation_history
                    (id INTEGER PRIMARY KEY,
                     category TEXT,
                     timestamp DATETIME,
                     correct_bin BOOLEAN)''')
        self.conn.commit()

    def setup_gui(self):
        # Create frames
        self.camera_frame = ttk.Frame(self.root)
        self.camera_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)
        
        # Camera view
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()
        
        # Detection results
        self.result_label = ttk.Label(self.info_frame, 
                                    text="Detection Results", 
                                    font=('Arial', 16, 'bold'))
        self.result_label.pack(pady=10)
        
        # Instructions
        self.instruction_text = tk.Text(self.info_frame, 
                                      height=10, width=40, 
                                      font=('Arial', 12))
        self.instruction_text.pack(pady=10)
        
        # Statistics
        self.stats_label = ttk.Label(self.info_frame, 
                                   text="Statistics", 
                                   font=('Arial', 16, 'bold'))
        self.stats_label.pack(pady=10)
        
        self.stats_text = tk.Text(self.info_frame, 
                                height=8, width=40, 
                                font=('Arial', 12))
        self.stats_text.pack(pady=10)
        
        # Control buttons
        self.controls_frame = ttk.Frame(self.info_frame)
        self.controls_frame.pack(pady=10)
        
        ttk.Button(self.controls_frame, 
                  text="Capture", 
                  command=self.capture_waste).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, 
                  text="View Report", 
                  command=self.show_report).pack(side=tk.LEFT, padx=5)

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            # Detect objects
            results = self.model(frame)
            
            # Draw detection boxes
            for result in results[0].boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result
                if score > 0.5:
                    cv2.rectangle(frame, 
                                (int(x1), int(y1)), 
                                (int(x2), int(y2)), 
                                (0, 255, 0), 2)
            
            # Convert to tkinter format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo
        
        self.root.after(10, self.update_camera)

    def capture_waste(self):
        ret, frame = self.cap.read()
        if ret:
            results = self.model(frame)
            self.process_detection(results[0])

    def process_detection(self, result):
        detected_items = []
        for box in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = box
            if score > 0.5:
                class_name = self.model.names[int(class_id)]
                detected_items.append(class_name)
                
                # Print detected class name
                print(f"YOLO detected: {class_name}")
                
                # Determine waste category
                category = self.classify_waste(class_name)
                
                # Update database
                self.update_database(category)
                
                # Show instructions
                self.show_instructions(category)
                
                # Draw label on frame
                self.result_label.config(text=f"Detected: {class_name}\nCategory: {category}")
        
        self.update_statistics()

    def classify_waste(self, item):
        # Enhanced classification logic with more items
        plastic_items = ['bottle', 'cup', 'plastic bag', 'container']
        paper_items = ['book', 'paper', 'box', 'notebook', 'magazine', 'newspaper']
        organic_items = ['apple', 'banana', 'orange', 'person', 'food']
        electronic_items = ['cell phone', 'laptop', 'keyboard', 'mouse', 'tv']
        metal_items = ['can', 'utensil', 'fork', 'spoon', 'knife']
        glass_items = ['wine glass', 'bottle', 'vase']
        
        if item.lower() in plastic_items:
            return 'plastic'
        elif item.lower() in paper_items:
            return 'paper'
        elif item.lower() in organic_items:
            return 'organic'
        elif item.lower() in electronic_items:
            return 'electronic'
        elif item.lower() in metal_items:
            return 'metal'
        elif item.lower() in glass_items:
            return 'glass'
        else:
            # Print detected item for debugging
            print(f"Detected item: {item}")
            return 'other'

    def process_detection(self, result):
        detected_items = []
        for box in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = box
            if score > 0.5:
                class_name = self.model.names[int(class_id)]
                detected_items.append(class_name)
                
                # Print detected class name
                print(f"YOLO detected: {class_name}")
                
                # Determine waste category
                category = self.classify_waste(class_name)
                
                # Update database
                self.update_database(category)
                
                # Show instructions
                self.show_instructions(category)
                
                # Draw label on frame
                self.result_label.config(text=f"Detected: {class_name}\nCategory: {category}")
        
        self.update_statistics()

    def show_instructions(self, category):
        if category in self.waste_categories:
            info = self.waste_categories[category]
            instructions = f"""
            Detected Waste: {category.upper()}
            
            Instructions:
            1. Place in: {info['bin']}
            2. Bin Color: {info['color']}
            
            Tips:
            - Clean and dry before disposal
            - Remove any non-{category} parts
            - Flatten if possible
            """
            self.instruction_text.delete(1.0, tk.END)
            self.instruction_text.insert(tk.END, instructions)

    def update_database(self, category):
        c = self.conn.cursor()
        c.execute("""INSERT INTO segregation_history 
                    (category, timestamp, correct_bin) 
                    VALUES (?, ?, ?)""", 
                 (category, datetime.now(), True))
        self.conn.commit()

    def update_statistics(self):
        c = self.conn.cursor()
        c.execute("""SELECT category, COUNT(*) 
                    FROM segregation_history 
                    GROUP BY category""")
        stats = c.fetchall()
        
        stats_text = "Segregation Statistics:\n\n"
        for category, count in stats:
            stats_text += f"{category.title()}: {count} items\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)

    def show_report(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Detailed Report")
        report_window.geometry("400x600")
        
        text_widget = tk.Text(report_window, font=('Arial', 12))
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        c = self.conn.cursor()
        c.execute("""SELECT category, timestamp, correct_bin 
                    FROM segregation_history 
                    ORDER BY timestamp DESC 
                    LIMIT 50""")
        records = c.fetchall()
        
        report_text = "Recent Segregation History:\n\n"
        for record in records:
            report_text += f"Category: {record[0]}\n"
            report_text += f"Time: {record[1]}\n"
            report_text += f"Correct Bin: {'Yes' if record[2] else 'No'}\n"
            report_text += "-" * 40 + "\n"
        
        text_widget.insert(tk.END, report_text)

    def run(self):
        self.root.mainloop()
        self.cap.release()
        self.conn.close()

if __name__ == "__main__":
    app = WasteSegregationAssistant()
    app.run()