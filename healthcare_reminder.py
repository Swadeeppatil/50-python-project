import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import datetime
import sqlite3
import cv2
import threading
import time
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
import json

class HealthcareReminder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Elderly Healthcare Reminder System")
        self.root.geometry("1200x800")
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # Initialize database
        self.init_database()
        
        # Initialize camera for presence detection
        self.camera_active = False
        self.setup_gui()
        
        # Reminder settings
        self.reminders = []
        self.load_reminders()
        
        # Start reminder checker thread
        self.checker_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.checker_thread.start()

    def init_database(self):
        self.conn = sqlite3.connect('healthcare.db')
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reminders
                    (id INTEGER PRIMARY KEY,
                     title TEXT,
                     time TEXT,
                     type TEXT,
                     status TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS caregiver
                    (id INTEGER PRIMARY KEY,
                     name TEXT,
                     email TEXT,
                     phone TEXT)''')
        self.conn.commit()

    def setup_gui(self):
        # Create main frames
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)
        
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)
        
        # Reminder input section
        self.setup_reminder_input()
        
        # Camera feed section
        self.setup_camera_feed()
        
        # Reminder list section
        self.setup_reminder_list()
        
        # Caregiver info section
        self.setup_caregiver_info()

    def setup_reminder_input(self):
        input_frame = ttk.LabelFrame(self.left_frame, text="Add New Reminder")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Time:").grid(row=1, column=0, padx=5, pady=5)
        self.time_entry = ttk.Entry(input_frame)
        self.time_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Type:").grid(row=2, column=0, padx=5, pady=5)
        self.type_combo = ttk.Combobox(input_frame, 
                                     values=["Medication", "Appointment", "Exercise", "Vital Check"])
        self.type_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Add Reminder", 
                  command=self.add_reminder).grid(row=3, column=0, columnspan=2, pady=10)

    def setup_camera_feed(self):
        camera_frame = ttk.LabelFrame(self.right_frame, text="Presence Detection")
        camera_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack()
        
        ttk.Button(camera_frame, text="Toggle Camera", 
                  command=self.toggle_camera).pack(pady=5)

    def setup_reminder_list(self):
        list_frame = ttk.LabelFrame(self.left_frame, text="Current Reminders")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.reminder_tree = ttk.Treeview(list_frame, 
                                        columns=("Time", "Type", "Status"),
                                        show="headings")
        self.reminder_tree.heading("Time", text="Time")
        self.reminder_tree.heading("Type", text="Type")
        self.reminder_tree.heading("Status", text="Status")
        self.reminder_tree.pack(fill=tk.BOTH, expand=True)

    def setup_caregiver_info(self):
        caregiver_frame = ttk.LabelFrame(self.left_frame, text="Caregiver Information")
        caregiver_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(caregiver_frame, text="Email:").pack(pady=2)
        self.caregiver_email = ttk.Entry(caregiver_frame)
        self.caregiver_email.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(caregiver_frame, text="Phone:").pack(pady=2)
        self.caregiver_phone = ttk.Entry(caregiver_frame)
        self.caregiver_phone.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(caregiver_frame, text="Save Caregiver Info", 
                  command=self.save_caregiver_info).pack(pady=5)

    def toggle_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            self.camera_active = True
            self.update_camera()
        else:
            self.camera_active = False
            self.cap.release()
            self.camera_label.configure(image='')

    def update_camera(self):
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (320, 240))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.camera_label.configure(image=photo)
                self.camera_label.image = photo
            self.root.after(10, self.update_camera)

    def add_reminder(self):
        title = self.title_entry.get()
        time_str = self.time_entry.get()
        reminder_type = self.type_combo.get()
        
        if not all([title, time_str, reminder_type]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        c = self.conn.cursor()
        c.execute("INSERT INTO reminders (title, time, type, status) VALUES (?, ?, ?, ?)",
                 (title, time_str, reminder_type, "Pending"))
        self.conn.commit()
        
        self.load_reminders()
        self.clear_inputs()
        
        messagebox.showinfo("Success", "Reminder added successfully")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.type_combo.set('')

    def load_reminders(self):
        for item in self.reminder_tree.get_children():
            self.reminder_tree.delete(item)
            
        c = self.conn.cursor()
        c.execute("SELECT title, time, type, status FROM reminders")
        for reminder in c.fetchall():
            self.reminder_tree.insert('', tk.END, values=reminder)

    def check_reminders(self):
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            c = self.conn.cursor()
            c.execute("SELECT * FROM reminders WHERE time = ? AND status = 'Pending'", (current_time,))
            due_reminders = c.fetchall()
            
            for reminder in due_reminders:
                self.trigger_reminder(reminder)
                c.execute("UPDATE reminders SET status = 'Completed' WHERE id = ?", (reminder[0],))
                self.conn.commit()
            
            self.load_reminders()
            time.sleep(60)

    def trigger_reminder(self, reminder):
        # Voice alert
        message = f"Time for {reminder[1]}"
        self.tts_engine.say(message)
        self.tts_engine.runAndWait()
        
        # Send email to caregiver
        self.send_caregiver_alert(reminder)

    def send_caregiver_alert(self, reminder):
        try:
            c = self.conn.cursor()
            c.execute("SELECT email FROM caregiver WHERE id = 1")
            caregiver_email = c.fetchone()
            
            if caregiver_email:
                msg = MIMEText(f"Reminder: {reminder[1]} at {reminder[2]}")
                msg['Subject'] = "Healthcare Reminder Alert"
                msg['From'] = "healthcare.system@example.com"
                msg['To'] = caregiver_email[0]
                
                # Configure your email settings here
                # server = smtplib.SMTP('smtp.gmail.com', 587)
                # server.starttls()
                # server.login("your_email@gmail.com", "your_password")
                # server.send_message(msg)
                # server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def save_caregiver_info(self):
        email = self.caregiver_email.get()
        phone = self.caregiver_phone.get()
        
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO caregiver (id, email, phone) VALUES (1, ?, ?)",
                 (email, phone))
        self.conn.commit()
        
        messagebox.showinfo("Success", "Caregiver information saved")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HealthcareReminder()
    app.run()