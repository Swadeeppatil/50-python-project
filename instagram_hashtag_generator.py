import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import threading
import json
import os
from datetime import datetime

class HashtagGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Hashtag Generator")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.video_path = None
        self.model = ResNet50(weights='imagenet')
        self.hashtag_categories = {
            'nature': ['#nature', '#naturephotography', '#naturelovers'],
            'food': ['#food', '#foodporn', '#foodie', '#instafood'],
            'sports': ['#sports', '#fitness', '#workout'],
            'fashion': ['#fashion', '#style', '#ootd'],
            'travel': ['#travel', '#wanderlust', '#travelgram'],
            'pets': ['#pets', '#dog', '#cat', '#animals'],
            'art': ['#art', '#artist', '#artwork'],
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel)
        
        # Upload section
        upload_frame = ttk.LabelFrame(left_panel, text="Upload Video", padding=5)
        upload_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(upload_frame, text="Select Video", 
                  command=self.upload_video).pack(fill=tk.X, pady=5)
        
        # Video info
        self.video_info = ttk.Label(upload_frame, text="No video selected")
        self.video_info.pack(fill=tk.X, pady=5)
        
        # Analysis options
        options_frame = ttk.LabelFrame(left_panel, text="Analysis Options", padding=5)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.analyze_frames = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Analyze video frames", 
                       variable=self.analyze_frames).pack(fill=tk.X)
        
        # Hashtag count
        ttk.Label(options_frame, text="Number of hashtags:").pack()
        self.hashtag_count = ttk.Spinbox(options_frame, from_=5, to=30, width=5)
        self.hashtag_count.set(15)
        self.hashtag_count.pack()
        
        # Action buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.analyze_btn = ttk.Button(action_frame, text="Generate Hashtags", 
                                    command=self.start_analysis)
        self.analyze_btn.pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="Copy Hashtags", 
                  command=self.copy_hashtags).pack(fill=tk.X, pady=2)
        
        ttk.Button(action_frame, text="Save Hashtags", 
                  command=self.save_hashtags).pack(fill=tk.X, pady=2)
        
        # Right panel
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel)
        
        # Preview
        preview_frame = ttk.LabelFrame(right_panel, text="Video Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(preview_frame, width=400, height=300)
        self.preview_canvas.pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(right_panel, text="Generated Hashtags", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.hashtag_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        self.hashtag_text.pack(fill=tk.BOTH, expand=True)
        
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            self.video_path = file_path
            self.show_video_info()
            self.display_preview()
            
    def show_video_info(self):
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            duration = frames / fps
            cap.release()
            
            info = f"Video: {os.path.basename(self.video_path)}\n"
            info += f"Duration: {int(duration)}s, Frames: {frames}, FPS: {fps}"
            self.video_info.config(text=info)
            
    def display_preview(self):
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frame.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(frame)
                self.preview_canvas.create_image(
                    200, 150, image=photo, anchor=tk.CENTER
                )
                self.preview_canvas.image = photo
            cap.release()
            
    def start_analysis(self):
        if not self.video_path:
            messagebox.showwarning("Warning", "Please select a video first!")
            return
            
        self.analyze_btn.config(state='disabled')
        threading.Thread(target=self.analyze_video, daemon=True).start()
        
    def analyze_video(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = total_frames // 10  # Analyze 10 frames
            
            predictions = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % sample_interval == 0:
                    # Prepare frame for model
                    frame = cv2.resize(frame, (224, 224))
                    frame = preprocess_input(frame)
                    frame = np.expand_dims(frame, axis=0)
                    
                    # Get predictions
                    preds = self.model.predict(frame)
                    pred_classes = decode_predictions(preds, top=5)[0]
                    predictions.extend([p[1] for p in pred_classes])
                
                frame_count += 1
            
            cap.release()
            
            # Generate hashtags
            self.generate_hashtags(predictions)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        finally:
            self.analyze_btn.config(state='normal')
            
    def generate_hashtags(self, predictions):
        hashtags = set()
        
        # Map predictions to hashtag categories
        for pred in predictions:
            for category, tags in self.hashtag_categories.items():
                if any(keyword in pred.lower() for keyword in category.split()):
                    hashtags.update(tags)
        
        # Add some general Instagram hashtags
        general_tags = ['#instagram', '#instagood', '#photooftheday']
        hashtags.update(general_tags)
        
        # Limit hashtags to specified count
        hashtags = list(hashtags)[:int(self.hashtag_count.get())]
        
        # Display hashtags
        self.hashtag_text.delete(1.0, tk.END)
        self.hashtag_text.insert(tk.END, ' '.join(hashtags))
        
    def copy_hashtags(self):
        hashtags = self.hashtag_text.get(1.0, tk.END).strip()
        if hashtags:
            self.root.clipboard_clear()
            self.root.clipboard_append(hashtags)
            messagebox.showinfo("Success", "Hashtags copied to clipboard!")
            
    def save_hashtags(self):
        hashtags = self.hashtag_text.get(1.0, tk.END).strip()
        if not hashtags:
            messagebox.showwarning("Warning", "No hashtags to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"hashtags_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(hashtags)
                messagebox.showinfo("Success", "Hashtags saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving hashtags: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HashtagGenerator(root)
    root.mainloop()