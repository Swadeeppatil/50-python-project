import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import cv2
import numpy as np
import threading
import time
import dlib
import mediapipe as mp
from PIL import Image, ImageTk
import json
import os
from datetime import datetime

class ExamProctor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Online Exam Proctor")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2C3E50')
        
        # Initialize detectors
        self.face_detector = dlib.get_frontal_face_detector()
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
        self.mp_pose = mp.solutions.pose.Pose()
        
        self.is_monitoring = False
        self.violations = []
        self.cap = None
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = tk.Frame(self.window, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Video feed frame
        video_frame = tk.LabelFrame(main_frame, text="Video Feed",
                                  bg='#2C3E50', fg='white')
        video_frame.pack(side=tk.LEFT, padx=5, pady=5, fill='both', expand=True)
        
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack(padx=5, pady=5)
        
        # Controls frame
        controls = tk.Frame(video_frame, bg='#2C3E50')
        controls.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(controls, text="Start Monitoring",
                  command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Stop Monitoring",
                  command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        
        # Violations log
        log_frame = tk.LabelFrame(main_frame, text="Violation Log",
                                bg='#2C3E50', fg='white')
        log_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill='both')
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=40, height=30,
                                                bg='#34495E', fg='white')
        self.log_text.pack(padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status = tk.Label(self.window, textvariable=self.status_var,
                         bg='#2C3E50', fg='white')
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
    def start_monitoring(self):
        if not self.is_monitoring:
            self.cap = cv2.VideoCapture(0)
            self.is_monitoring = True
            self.status_var.set("Monitoring active")
            threading.Thread(target=self.monitor_feed, daemon=True).start()
            
    def stop_monitoring(self):
        self.is_monitoring = False
        if self.cap:
            self.cap.release()
        self.status_var.set("Monitoring stopped")
        
    def monitor_feed(self):
        face_time = time.time()
        no_face_duration = 0
        last_violation_time = time.time()
        
        while self.is_monitoring:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Face detection
            faces = self.face_detector(rgb_frame)
            
            # Face mesh detection
            face_mesh_results = self.mp_face_mesh.process(rgb_frame)
            
            # Pose detection
            pose_results = self.mp_pose.process(rgb_frame)
            
            current_time = time.time()
            
            # Check for violations
            if len(faces) == 0:
                if current_time - face_time > 3:  # No face for 3 seconds
                    if current_time - last_violation_time > 5:  # Limit logging frequency
                        self.log_violation("No face detected")
                        last_violation_time = current_time
                no_face_duration += 1
            else:
                face_time = current_time
                no_face_duration = 0
                
                # Check for multiple faces
                if len(faces) > 1:
                    if current_time - last_violation_time > 5:
                        self.log_violation(f"Multiple faces detected ({len(faces)})")
                        last_violation_time = current_time
                        
            # Check head pose
            if pose_results.pose_landmarks:
                self.check_head_position(pose_results.pose_landmarks, current_time,
                                      last_violation_time)
                
            # Draw detection results
            self.draw_detections(frame, faces, face_mesh_results, pose_results)
            
            # Update GUI
            self.update_video_feed(frame)
            
        cv2.destroyAllWindows()
        
    def check_head_position(self, landmarks, current_time, last_violation_time):
        # Get head keypoints
        nose = landmarks.landmark[0]
        left_ear = landmarks.landmark[7]
        right_ear = landmarks.landmark[8]
        
        # Calculate head rotation
        head_rotation = abs(left_ear.x - right_ear.x)
        
        # Check for significant head rotation
        if head_rotation > 0.3:  # Threshold for head turning
            if current_time - last_violation_time > 5:
                self.log_violation("Suspicious head movement detected")
                return current_time
        return last_violation_time
        
    def draw_detections(self, frame, faces, face_mesh_results, pose_results):
        # Draw face detections
        for face in faces:
            x, y = face.left(), face.top()
            w, h = face.right() - x, face.bottom() - y
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        # Draw face mesh
        if face_mesh_results.multi_face_landmarks:
            for face_landmarks in face_mesh_results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    h, w, _ = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                    
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS
            )
            
    def update_video_feed(self, frame):
        # Convert frame to PhotoImage
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
    def log_violation(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.violations.append(log_entry)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def save_violations(self):
        if self.violations:
            filename = f"violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.writelines(self.violations)
                
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
        
    def on_closing(self):
        self.stop_monitoring()
        self.save_violations()
        self.window.destroy()

if __name__ == "__main__":
    app = ExamProctor()
    app.run()