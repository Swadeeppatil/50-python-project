import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
import os
import random

class EyeHealthAnalyzer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Advanced Eye Health Analyzer")
        self.window.geometry("1400x900")
        self.window.configure(bg='#2C3E50')
        
        # Initialize components
        self.camera = None
        self.recording = False
        self.analysis_active = False
        self.scan_progress = 0
        self.patient_data = {}
        
        # Load classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        self.create_gui()
        self.load_patient_history()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Patient Info and Controls
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side='left', fill='y', padx=5)
        
        # Patient Information
        patient_frame = ttk.LabelFrame(left_panel, text="Patient Information")
        patient_frame.pack(fill='x', pady=5)
        
        ttk.Label(patient_frame, text="Patient ID:").pack(pady=2)
        self.patient_id = ttk.Entry(patient_frame)
        self.patient_id.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(patient_frame, text="Name:").pack(pady=2)
        self.patient_name = ttk.Entry(patient_frame)
        self.patient_name.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(patient_frame, text="Age:").pack(pady=2)
        self.patient_age = ttk.Entry(patient_frame)
        self.patient_age.pack(fill='x', padx=5, pady=2)
        
        # Control buttons
        controls = ttk.Frame(left_panel)
        controls.pack(fill='x', pady=10)
        
        ttk.Button(controls, text="Start Analysis",
                  command=self.start_analysis).pack(fill='x', pady=2)
        ttk.Button(controls, text="Stop Analysis",
                  command=self.stop_analysis).pack(fill='x', pady=2)
        ttk.Button(controls, text="Save Results",
                  command=self.save_results).pack(fill='x', pady=2)
        
        # Center panel - Live View and Analysis
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        # Live camera view
        self.camera_label = ttk.Label(center_panel)
        self.camera_label.pack(pady=5)
        
        # OCT scan simulation
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, center_panel)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Right panel - Results and Metrics
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side='right', fill='y', padx=5)
        
        # Analysis results
        results_frame = ttk.LabelFrame(right_panel, text="Analysis Results")
        results_frame.pack(fill='x', pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Metrics display
        metrics_frame = ttk.LabelFrame(right_panel, text="Key Metrics")
        metrics_frame.pack(fill='x', pady=5)
        
        self.metrics = {
            'Corneal Thickness': tk.StringVar(),
            'Retinal Thickness': tk.StringVar(),
            'Cup-to-Disc Ratio': tk.StringVar(),
            'IOP': tk.StringVar()
        }
        
        for metric, var in self.metrics.items():
            frame = ttk.Frame(metrics_frame)
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=f"{metric}:").pack(side='left')
            ttk.Label(frame, textvariable=var).pack(side='right')
            
    def start_analysis(self):
        if not self.patient_id.get():
            messagebox.showerror("Error", "Please enter patient ID")
            return
            
        self.analysis_active = True
        self.camera = cv2.VideoCapture(0)
        self.update_camera()
        self.simulate_oct_scan()
        
    def update_camera(self):
        if self.analysis_active and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Eye detection and analysis
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
                        self.analyze_eye_region(roi_color[ey:ey+eh, ex:ex+ew])
                
                # Update display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
                
            self.window.after(10, self.update_camera)
            
    def simulate_oct_scan(self):
        if self.analysis_active:
            # Simulate OCT data
            x = np.linspace(0, 10, 100)
            noise = np.random.normal(0, 0.1, 100)
            retina_layer = 2 * np.sin(x) + 5 + noise
            
            # Update plots
            self.ax1.clear()
            self.ax2.clear()
            
            self.ax1.plot(x, retina_layer)
            self.ax1.set_title('Retinal Layer Analysis')
            
            # Thickness map
            thickness_data = np.random.normal(300, 20, (20, 20))
            self.ax2.imshow(thickness_data, cmap='jet')
            self.ax2.set_title('Thickness Map')
            
            self.canvas.draw()
            
            # Update metrics
            self.update_metrics()
            
            self.window.after(1000, self.simulate_oct_scan)
            
    def analyze_eye_region(self, eye_region):
        # Simulate eye analysis
        if eye_region.size > 0:
            # Calculate average intensity
            avg_intensity = np.mean(eye_region)
            
            # Update results
            self.results_text.insert(tk.END, 
                f"Analysis timestamp: {datetime.now().strftime('%H:%M:%S')}\n"
                f"Average intensity: {avg_intensity:.2f}\n"
                f"Region size: {eye_region.shape}\n\n")
            self.results_text.see(tk.END)
            
    def update_metrics(self):
        # Simulate metric updates
        self.metrics['Corneal Thickness'].set(f"{random.uniform(540, 560):.1f} μm")
        self.metrics['Retinal Thickness'].set(f"{random.uniform(200, 250):.1f} μm")
        self.metrics['Cup-to-Disc Ratio'].set(f"{random.uniform(0.3, 0.5):.2f}")
        self.metrics['IOP'].set(f"{random.uniform(12, 20):.1f} mmHg")
        
    def save_results(self):
        if not self.patient_id.get():
            messagebox.showerror("Error", "No patient ID")
            return
            
        results = {
            'patient_id': self.patient_id.get(),
            'name': self.patient_name.get(),
            'age': self.patient_age.get(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {k: v.get() for k, v in self.metrics.items()},
            'analysis': self.results_text.get(1.0, tk.END)
        }
        
        # Save to file
        os.makedirs('patient_data', exist_ok=True)
        filename = f"patient_data/{self.patient_id.get()}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
            
        messagebox.showinfo("Success", "Results saved successfully")
        
    def load_patient_history(self):
        if os.path.exists('patient_data'):
            for file in os.listdir('patient_data'):
                if file.endswith('.json'):
                    with open(f"patient_data/{file}", 'r') as f:
                        data = json.load(f)
                        self.patient_data[data['patient_id']] = data
                        
    def stop_analysis(self):
        self.analysis_active = False
        if self.camera is not None:
            self.camera.release()
            
    def run(self):
        self.window.mainloop()
        
    def __del__(self):
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()

if __name__ == "__main__":
    app = EyeHealthAnalyzer()
    app.run()