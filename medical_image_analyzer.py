import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage import filters, measure, segmentation
import pandas as pd
from datetime import datetime
import json
import os

class MedicalImageAnalyzer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Medical Image Analysis System")
        self.window.geometry("1400x900")
        self.window.configure(bg='#2E4053')
        
        # Initialize variables
        self.current_image = None
        self.processed_image = None
        self.analysis_results = {}
        self.model = None
        
        # Load ML model (placeholder)
        self.load_ml_model()
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Panel - Image Display and Controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Image display
        self.image_label = ttk.Label(left_panel)
        self.image_label.pack(pady=10)
        
        # Control buttons
        controls = ttk.Frame(left_panel)
        controls.pack(fill='x', pady=10)
        
        ttk.Button(controls, text="Load Image",
                  command=self.load_image).pack(side='left', padx=5)
        ttk.Button(controls, text="Process Image",
                  command=self.process_image).pack(side='left', padx=5)
        ttk.Button(controls, text="Detect Anomalies",
                  command=self.detect_anomalies).pack(side='left', padx=5)
        ttk.Button(controls, text="Save Results",
                  command=self.save_results).pack(side='left', padx=5)
        
        # Right Panel - Analysis and Results
        right_panel = ttk.Frame(main_frame, width=400)
        right_panel.pack(side='right', fill='both', padx=5)
        
        # Analysis options
        options_frame = ttk.LabelFrame(right_panel, text="Analysis Options")
        options_frame.pack(fill='x', pady=5)
        
        self.analysis_type = tk.StringVar(value="tumor")
        ttk.Radiobutton(options_frame, text="Tumor Detection",
                       variable=self.analysis_type,
                       value="tumor").pack(side='left', padx=10)
        ttk.Radiobutton(options_frame, text="Fracture Detection",
                       variable=self.analysis_type,
                       value="fracture").pack(side='left', padx=10)
        
        # Results display
        results_frame = ttk.LabelFrame(right_panel, text="Analysis Results")
        results_frame.pack(fill='both', expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Visualization
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, right_panel)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.dcm")])
        
        if file_path:
            try:
                # Load and display image
                self.current_image = cv2.imread(file_path)
                self.display_image(self.current_image)
                self.results_text.insert(tk.END, f"Loaded image: {file_path}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_image(self, image):
        if image is not None:
            # Resize for display
            height, width = image.shape[:2]
            max_size = 500
            scale = max_size / max(height, width)
            
            if scale < 1:
                image = cv2.resize(image, None, fx=scale, fy=scale)
                
            # Convert to PIL format
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(image_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)
            
    def process_image(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        # Image preprocessing
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            
            # Apply filtering
            denoised = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Edge detection
            edges = filters.sobel(enhanced)
            
            # Update visualization
            self.ax1.clear()
            self.ax1.imshow(enhanced, cmap='gray')
            self.ax1.set_title('Enhanced Image')
            
            self.ax2.clear()
            self.ax2.imshow(edges, cmap='gray')
            self.ax2.set_title('Edge Detection')
            
            self.canvas.draw()
            
            self.processed_image = enhanced
            self.results_text.insert(tk.END, "Image processing completed\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            
    def detect_anomalies(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "Please process the image first")
            return
            
        try:
            # Segmentation
            thresh = filters.threshold_otsu(self.processed_image)
            binary = self.processed_image > thresh
            
            # Label regions
            labeled_image = measure.label(binary)
            regions = measure.regionprops(labeled_image)
            
            # Analyze regions
            anomalies = []
            for region in regions:
                if region.area > 100:  # Filter small regions
                    anomalies.append({
                        'area': region.area,
                        'perimeter': region.perimeter,
                        'centroid': region.centroid
                    })
            
            # Update results
            self.results_text.insert(tk.END, 
                f"\nDetected {len(anomalies)} potential anomalies\n")
            
            for i, anomaly in enumerate(anomalies):
                self.results_text.insert(tk.END,
                    f"Anomaly {i+1}:\n"
                    f"Area: {anomaly['area']:.2f}\n"
                    f"Perimeter: {anomaly['perimeter']:.2f}\n"
                    f"Location: ({anomaly['centroid'][0]:.1f}, "
                    f"{anomaly['centroid'][1]:.1f})\n\n")
                    
            # Visualize results
            self.ax1.clear()
            self.ax1.imshow(self.processed_image, cmap='gray')
            self.ax1.set_title('Processed Image')
            
            self.ax2.clear()
            self.ax2.imshow(labeled_image, cmap='nipy_spectral')
            self.ax2.set_title('Detected Anomalies')
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def load_ml_model(self):
        # Placeholder for ML model loading
        try:
            # self.model = load_model('medical_analysis_model.h5')
            pass
        except Exception as e:
            print(f"Model loading failed: {str(e)}")
            
    def save_results(self):
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No results to save")
            return
            
        try:
            # Create results directory
            os.makedirs('analysis_results', exist_ok=True)
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_results/results_{timestamp}.json"
            
            results = {
                'timestamp': timestamp,
                'analysis_type': self.analysis_type.get(),
                'results': self.results_text.get(1.0, tk.END),
            }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=4)
                
            # Save visualization
            self.fig.savefig(f"analysis_results/visualization_{timestamp}.png")
            
            messagebox.showinfo("Success", "Results saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MedicalImageAnalyzer()
    app.run()