import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import cv2
import threading
import time
import json
import random
import speech_recognition as sr
import pyttsx3
import numpy as np
from PIL import Image, ImageTk
import os
from datetime import datetime

class AIInterviewer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AI Interview System")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2C3E50')
        
        # Initialize variables
        self.recording = False
        self.interview_started = False
        self.current_question = 0
        self.video_capture = None
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # Load interview questions
        self.questions = {
            "Technical": [
                "Tell me about your experience with Python programming.",
                "How do you handle error handling in your code?",
                "Explain object-oriented programming concepts.",
                "What are your thoughts on code optimization?",
                "Describe your experience with databases."
            ],
            "HR": [
                "Tell me about yourself.",
                "Why should we hire you?",
                "Where do you see yourself in 5 years?",
                "What are your strengths and weaknesses?",
                "How do you handle work pressure?"
            ],
            "Behavioral": [
                "Describe a challenging project you worked on.",
                "How do you handle conflicts in a team?",
                "Give an example of your leadership experience.",
                "How do you prioritize your tasks?",
                "Tell me about a time you failed and learned from it."
            ]
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Left panel - Video feed and controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Video frame
        self.video_label = ttk.Label(left_panel)
        self.video_label.pack(pady=10)
        
        # Controls
        controls = ttk.Frame(left_panel)
        controls.pack(fill='x', pady=10)
        
        self.start_button = ttk.Button(controls, text="Start Interview",
                                     command=self.start_interview)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(controls, text="Stop Interview",
                                    command=self.stop_interview, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Right panel - Interview content
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Interview type selection
        type_frame = ttk.LabelFrame(right_panel, text="Interview Type")
        type_frame.pack(fill='x', pady=5)
        
        self.interview_type = tk.StringVar(value="Technical")
        for type_ in self.questions.keys():
            ttk.Radiobutton(type_frame, text=type_, value=type_,
                          variable=self.interview_type).pack(side='left', padx=10)
        
        # Current question display
        question_frame = ttk.LabelFrame(right_panel, text="Current Question")
        question_frame.pack(fill='x', pady=5)
        
        self.question_label = ttk.Label(question_frame, text="Press Start to begin",
                                      wraplength=400)
        self.question_label.pack(pady=10)
        
        # Answer analysis
        analysis_frame = ttk.LabelFrame(right_panel, text="Answer Analysis")
        analysis_frame.pack(fill='both', expand=True, pady=5)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=10)
        self.analysis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Feedback
        feedback_frame = ttk.LabelFrame(right_panel, text="Feedback")
        feedback_frame.pack(fill='x', pady=5)
        
        self.feedback_text = scrolledtext.ScrolledText(feedback_frame, height=5)
        self.feedback_text.pack(fill='x', padx=5, pady=5)
        
    def start_interview(self):
        self.recording = True
        self.interview_started = True
        self.current_question = 0
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Start video capture
        self.video_capture = cv2.VideoCapture(0)
        
        # Create output directory
        os.makedirs('interviews', exist_ok=True)
        self.session_dir = f"interviews/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.session_dir)
        
        # Start video recording thread
        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()
        
        # Start interview questions
        self.ask_next_question()
        
    def record_video(self):
        output_path = f"{self.session_dir}/interview.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (640,480))
        
        while self.recording:
            ret, frame = self.video_capture.read()
            if ret:
                # Save frame
                out.write(frame)
                
                # Display frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
        out.release()
        
    def ask_next_question(self):
        if self.current_question < len(self.questions[self.interview_type.get()]):
            question = self.questions[self.interview_type.get()][self.current_question]
            self.question_label.config(text=question)
            
            # Text-to-speech
            self.engine.say(question)
            self.engine.runAndWait()
            
            # Start listening for answer
            self.listen_thread = threading.Thread(target=self.listen_for_answer)
            self.listen_thread.start()
        else:
            self.stop_interview()
            
    def listen_for_answer(self):
        with sr.Microphone() as source:
            try:
                self.analysis_text.insert(tk.END, "Listening for your answer...\n")
                audio = self.recognizer.listen(source, timeout=10)
                text = self.recognizer.recognize_google(audio)
                
                self.analyze_answer(text)
                self.current_question += 1
                self.ask_next_question()
                
            except sr.WaitTimeoutError:
                self.analysis_text.insert(tk.END, "No answer detected. Moving to next question.\n")
                self.current_question += 1
                self.ask_next_question()
                
            except Exception as e:
                self.analysis_text.insert(tk.END, f"Error: {str(e)}\n")
                
    def analyze_answer(self, answer):
        # Simple answer analysis
        self.analysis_text.insert(tk.END, f"\nYour answer: {answer}\n")
        
        # Word count analysis
        words = len(answer.split())
        self.analysis_text.insert(tk.END, f"Word count: {words}\n")
        
        # Confidence analysis
        confidence_words = ['confident', 'sure', 'definitely', 'absolutely']
        confidence_score = sum(1 for word in confidence_words if word.lower() in answer.lower())
        
        # Provide feedback
        feedback = "Feedback:\n"
        if words < 20:
            feedback += "- Try to provide more detailed answers\n"
        if confidence_score < 2:
            feedback += "- Try to sound more confident in your responses\n"
        if words > 100:
            feedback += "- Try to be more concise\n"
            
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.insert(tk.END, feedback)
        
    def stop_interview(self):
        self.recording = False
        self.interview_started = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        if self.video_capture:
            self.video_capture.release()
            
        # Save interview summary
        self.save_interview_summary()
        messagebox.showinfo("Interview Complete", 
                          "Interview session has been saved. Check the interviews folder.")
        
    def save_interview_summary(self):
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": self.interview_type.get(),
            "feedback": self.feedback_text.get(1.0, tk.END),
            "analysis": self.analysis_text.get(1.0, tk.END)
        }
        
        with open(f"{self.session_dir}/summary.json", 'w') as f:
            json.dump(summary, f, indent=4)
            
    def run(self):
        self.window.mainloop()
        
    def __del__(self):
        if self.video_capture:
            self.video_capture.release()

if __name__ == "__main__":
    app = AIInterviewer()
    app.run()