import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import speech_recognition as sr
import pyttsx3
import cv2
import threading
import json
import os
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import random

class EnglishTutor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("English Speaking Tutor")
        self.window.geometry("1280x800")
        self.window.configure(bg='#F0F8FF')
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Session variables
        self.recording = False
        self.practice_active = False
        self.scores = []
        self.topics = [
            "Self Introduction",
            "Daily Routine",
            "Hobbies",
            "Future Plans",
            "Favorite Movies",
            "Travel Experiences",
            "Food and Cuisine",
            "Technology",
            "Environment",
            "Education"
        ]
        
        # Load previous progress
        self.load_progress()
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left Panel - Video and Controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Video display
        self.video_label = ttk.Label(left_panel)
        self.video_label.pack(pady=10)
        
        # Controls
        controls = ttk.Frame(left_panel)
        controls.pack(fill='x', pady=10)
        
        ttk.Button(controls, text="Start Practice",
                  command=self.start_practice).pack(side='left', padx=5)
        ttk.Button(controls, text="Stop Practice",
                  command=self.stop_practice).pack(side='left', padx=5)
        
        # Topic selection
        topic_frame = ttk.LabelFrame(left_panel, text="Practice Topics")
        topic_frame.pack(fill='x', pady=5)
        
        self.topic_var = tk.StringVar(value=self.topics[0])
        topic_menu = ttk.OptionMenu(topic_frame, self.topic_var, *self.topics)
        topic_menu.pack(fill='x', padx=5, pady=5)
        
        # Right Panel - Analysis and Progress
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Speech text
        text_frame = ttk.LabelFrame(right_panel, text="Your Speech")
        text_frame.pack(fill='x', pady=5)
        
        self.speech_text = scrolledtext.ScrolledText(text_frame, height=6)
        self.speech_text.pack(fill='x', padx=5, pady=5)
        
        # Analysis
        analysis_frame = ttk.LabelFrame(right_panel, text="Analysis")
        analysis_frame.pack(fill='both', expand=True, pady=5)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=8)
        self.analysis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Progress graph
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, right_panel)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.update_progress_graph()
        
    def start_practice(self):
        self.practice_active = True
        self.recording = True
        
        # Start video capture
        self.video_capture = cv2.VideoCapture(0)
        
        # Start video thread
        self.video_thread = threading.Thread(target=self.update_video)
        self.video_thread.start()
        
        # Start practice session
        self.practice_thread = threading.Thread(target=self.practice_session)
        self.practice_thread.start()
        
    def update_video(self):
        while self.recording:
            ret, frame = self.video_capture.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
    def practice_session(self):
        topic = self.topic_var.get()
        self.engine.say(f"Let's practice speaking about {topic}")
        self.engine.say("Please speak for about 1 minute")
        self.engine.runAndWait()
        
        with sr.Microphone() as source:
            try:
                self.speech_text.delete(1.0, tk.END)
                self.speech_text.insert(tk.END, "Listening...\n")
                
                audio = self.recognizer.listen(source, timeout=60)
                text = self.recognizer.recognize_google(audio)
                
                self.speech_text.delete(1.0, tk.END)
                self.speech_text.insert(tk.END, text)
                
                self.analyze_speech(text)
                
            except Exception as e:
                self.speech_text.insert(tk.END, f"\nError: {str(e)}")
                
    def analyze_speech(self, text):
        # Word count
        words = text.split()
        word_count = len(words)
        
        # Vocabulary diversity
        unique_words = len(set(words))
        
        # Basic grammar check (simple implementation)
        grammar_score = self.check_grammar(text)
        
        # Fluency score (words per minute)
        fluency_score = word_count / 1  # 1 minute session
        
        # Calculate overall score
        overall_score = (grammar_score + (fluency_score/30) + (unique_words/word_count * 100)) / 3
        
        # Update analysis
        analysis = f"""Speech Analysis:
        - Words spoken: {word_count}
        - Unique words: {unique_words}
        - Vocabulary diversity: {(unique_words/word_count*100):.2f}%
        - Fluency (words/minute): {fluency_score:.2f}
        - Grammar score: {grammar_score:.2f}%
        - Overall score: {overall_score:.2f}%
        """
        
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, analysis)
        
        # Save score
        self.scores.append(overall_score)
        self.save_progress()
        self.update_progress_graph()
        
    def check_grammar(self, text):
        # Simple grammar checking (can be enhanced with NLP libraries)
        sentences = text.split('.')
        score = 0
        
        for sentence in sentences:
            if sentence.strip():
                words = sentence.strip().split()
                if words:
                    # Check for capitalization
                    if words[0][0].isupper():
                        score += 1
                    # Check for minimum length
                    if len(words) >= 3:
                        score += 1
                        
        return (score / (len(sentences) * 2)) * 100 if sentences else 0
        
    def update_progress_graph(self):
        self.ax.clear()
        if self.scores:
            self.ax.plot(self.scores, marker='o')
            self.ax.set_title('Speaking Progress')
            self.ax.set_xlabel('Practice Sessions')
            self.ax.set_ylabel('Overall Score')
            self.ax.grid(True)
        self.canvas.draw()
        
    def save_progress(self):
        data = {
            'scores': self.scores,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open('speaking_progress.json', 'w') as f:
            json.dump(data, f)
            
    def load_progress(self):
        try:
            with open('speaking_progress.json', 'r') as f:
                data = json.load(f)
                self.scores = data.get('scores', [])
        except FileNotFoundError:
            self.scores = []
            
    def stop_practice(self):
        self.recording = False
        self.practice_active = False
        if hasattr(self, 'video_capture'):
            self.video_capture.release()
            
    def run(self):
        self.window.mainloop()
        
    def __del__(self):
        if hasattr(self, 'video_capture'):
            self.video_capture.release()

if __name__ == "__main__":
    app = EnglishTutor()
    app.run()