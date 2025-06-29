import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import json
from datetime import datetime
import os

class EyeTestApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Eye Vision Test")
        self.window.geometry("1200x800")
        self.window.configure(bg='#FFFFFF')
        
        # Initialize variables
        self.current_distance = 20  # feet
        self.current_size = 100
        self.test_active = False
        self.results = []
        self.letters = 'ABCDEFGHKNPQRSUVZ'  # Snellen chart letters
        
        # Camera setup
        self.camera = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        self.create_gui()
        self.load_history()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Camera feed and controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Camera feed
        self.camera_label = ttk.Label(left_panel)
        self.camera_label.pack(pady=10)
        
        # Controls
        controls = ttk.Frame(left_panel)
        controls.pack(fill='x', pady=10)
        
        ttk.Button(controls, text="Start Test",
                  command=self.start_test).pack(side='left', padx=5)
        ttk.Button(controls, text="Stop Test",
                  command=self.stop_test).pack(side='left', padx=5)
        
        # Right panel - Test and Results
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Test display
        self.test_canvas = tk.Canvas(right_panel, width=400, height=300,
                                   bg='white')
        self.test_canvas.pack(pady=10)
        
        # Response buttons
        response_frame = ttk.Frame(right_panel)
        response_frame.pack(fill='x', pady=10)
        
        ttk.Button(response_frame, text="Correct",
                  command=lambda: self.record_response(True)).pack(side='left', padx=5)
        ttk.Button(response_frame, text="Incorrect",
                  command=lambda: self.record_response(False)).pack(side='left', padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(right_panel, text="Test Results")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def start_test(self):
        self.test_active = True
        self.camera = cv2.VideoCapture(0)
        self.update_camera()
        self.next_test()
        
    def update_camera(self):
        if self.test_active:
            ret, frame = self.camera.read()
            if ret:
                # Detect face and eyes
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey),
                                    (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Convert to tkinter format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
            self.window.after(10, self.update_camera)
            
    def next_test(self):
        if not self.test_active:
            return
            
        # Clear canvas
        self.test_canvas.delete('all')
        
        # Generate random letter
        letter = random.choice(self.letters)
        
        # Draw letter
        self.test_canvas.create_text(200, 150, text=letter,
                                   font=('Arial', self.current_size),
                                   fill='black')
                                   
    def record_response(self, correct):
        if not self.test_active:
            return
            
        # Record result
        result = {
            'distance': self.current_distance,
            'size': self.current_size,
            'correct': correct,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.results.append(result)
        
        # Adjust test difficulty
        if correct:
            self.current_size = max(20, self.current_size - 10)
        else:
            self.current_size = min(100, self.current_size + 10)
            
        # Calculate vision score
        vision_score = self.calculate_vision_score()
        
        # Update results display
        self.update_results(vision_score)
        
        # Save results
        self.save_history()
        
        # Next test
        self.next_test()
        
    def calculate_vision_score(self):
        if not self.results:
            return "20/20"
            
        # Simple calculation based on smallest correctly identified size
        correct_results = [r for r in self.results if r['correct']]
        if not correct_results:
            return "20/200+"
            
        smallest_size = min(r['size'] for r in correct_results)
        
        # Map size to vision score (simplified)
        size_to_score = {
            20: "20/20",
            30: "20/30",
            40: "20/40",
            50: "20/50",
            60: "20/70",
            70: "20/100",
            80: "20/150",
            90: "20/180",
            100: "20/200"
        }
        
        return size_to_score.get(smallest_size, "20/200+")
        
    def update_results(self, vision_score):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Vision Score: {vision_score}\n\n")
        self.results_text.insert(tk.END, "Recent Tests:\n")
        
        for result in reversed(self.results[-5:]):
            self.results_text.insert(tk.END,
                f"Time: {result['timestamp']}\n"
                f"Distance: {result['distance']} feet\n"
                f"Size: {result['size']}\n"
                f"Result: {'Correct' if result['correct'] else 'Incorrect'}\n\n")
                
    def save_history(self):
        data = {
            'results': self.results,
            'last_test': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('eye_test_history.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    def load_history(self):
        try:
            with open('eye_test_history.json', 'r') as f:
                data = json.load(f)
                self.results = data.get('results', [])
        except FileNotFoundError:
            self.results = []
            
    def stop_test(self):
        self.test_active = False
        if self.camera is not None:
            self.camera.release()
            
    def run(self):
        self.window.mainloop()
        
    def __del__(self):
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()

if __name__ == "__main__":
    app = EyeTestApp()
    app.run()