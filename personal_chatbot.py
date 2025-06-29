import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import random
import datetime
import webbrowser
import os

class PersonalChatbot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Personal Assistant")
        self.window.geometry("600x700")
        self.window.configure(bg='#2C3E50')
        
        # Load responses
        self.responses = {
            "hello": ["Hi!", "Hello!", "Hey there!", "Greetings!"],
            "how are you": ["I'm doing great!", "I'm fine, thanks!", "All good!"],
            "time": ["Current time is: " + datetime.datetime.now().strftime("%H:%M:%S")],
            "date": ["Today's date is: " + datetime.datetime.now().strftime("%Y-%m-%d")],
            "bye": ["Goodbye!", "See you later!", "Bye!"],
            "name": ["I'm BlackBox, your personal assistant!"],
            "weather": ["I can't check weather yet, but I'm learning!"],
            "help": ["I can help with:\n- Basic conversation\n- Time and date\n- Opening websites\n- Simple calculations"]
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, 
                                                 width=50, height=30,
                                                 bg='#34495E', fg='white',
                                                 font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.window, bg='#2C3E50')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input field
        self.input_field = tk.Entry(input_frame, width=40, font=("Arial", 12))
        self.input_field.pack(side=tk.LEFT, padx=5)
        self.input_field.bind("<Return>", lambda e: self.process_input())
        
        # Send button
        send_button = ttk.Button(input_frame, text="Send", command=self.process_input)
        send_button.pack(side=tk.LEFT, padx=5)
        
        # Welcome message
        self.add_message("BlackBox: Hello! How can I help you today?")
        
    def add_message(self, message):
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.see(tk.END)
        
    def process_input(self):
        user_input = self.input_field.get().lower().strip()
        self.input_field.delete(0, tk.END)
        
        if not user_input:
            return
            
        # Display user input
        self.add_message(f"You: {user_input}")
        
        # Process commands
        if "open" in user_input and "website" in user_input:
            try:
                url = user_input.split("website")[-1].strip()
                if not url.startswith("http"):
                    url = "https://" + url
                webbrowser.open(url)
                response = f"Opening {url}"
            except:
                response = "Sorry, I couldn't open that website."
                
        elif "calculate" in user_input:
            try:
                expression = user_input.replace("calculate", "").strip()
                result = eval(expression)
                response = f"Result: {result}"
            except:
                response = "Sorry, I couldn't perform that calculation."
                
        else:
            # Check for matching responses
            response = None
            for key in self.responses:
                if key in user_input:
                    response = random.choice(self.responses[key])
                    break
                    
            if not response:
                response = "I'm not sure how to respond to that yet."
        
        # Display bot response
        self.add_message(f"BlackBox: {response}")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    chatbot = PersonalChatbot()
    chatbot.run()