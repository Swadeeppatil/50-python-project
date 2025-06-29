import tkinter as tk
from tkinter import scrolledtext, ttk
import json
from datetime import datetime

class HealthAdvisorBot:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Personal Health Advisor")
        self.window.geometry("1000x700")
        self.window.configure(bg='#1E2F3E')
        
        # Nutrition database
        self.food_data = {
            'apple': {
                'calories': 95,
                'protein': '0.5g',
                'carbs': '25g',
                'fat': '0.3g',
                'sugar': '19g',
                'benefits': ['Heart health', 'Blood sugar control', 'Antioxidants'],
                'recommended_age': 'all'
            },
            'chicken breast': {
                'calories': 165,
                'protein': '31g',
                'carbs': '0g',
                'fat': '3.6g',
                'sugar': '0g',
                'benefits': ['Protein source', 'Muscle building', 'Low fat'],
                'recommended_age': 'all'
            },
            'spinach': {
                'calories': 23,
                'protein': '2.9g',
                'carbs': '3.6g',
                'fat': '0.4g',
                'sugar': '0.4g',
                'benefits': ['Iron rich', 'Eye health', 'Blood pressure'],
                'recommended_age': 'all'
            }
             
        }
        
        # Age-based recommendations
        self.age_recommendations = {
            'child': {
                'recommended': ['milk', 'fruits', 'vegetables', 'eggs'],
                'avoid': ['caffeine', 'processed sugar', 'fast food'],
                'daily_calories': '1600-2000'
            },
            'teen': {
                'recommended': ['protein rich foods', 'calcium rich foods', 'whole grains'],
                'avoid': ['excess sugar', 'energy drinks'],
                'daily_calories': '2000-2800'
            },
            'adult': {
                'recommended': ['lean proteins', 'vegetables', 'whole grains', 'healthy fats'],
                'avoid': ['excess salt', 'processed foods', 'sugary drinks'],
                'daily_calories': '2000-2600'
            },
            'senior': {
                'recommended': ['calcium rich foods', 'fiber rich foods', 'lean proteins'],
                'avoid': ['high sodium foods', 'saturated fats'],
                'daily_calories': '1800-2200'
            }
        }
        
        self.create_gui()
        
    def create_gui(self):
        # Title
        title = tk.Label(self.window, text="🥗 Personal Health Advisor",
                        font=("Helvetica", 24, "bold"), bg='#1E2F3E', fg='#00FF00')
        title.pack(pady=10)
        
        # Input Frame
        input_frame = tk.Frame(self.window, bg='#1E2F3E')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Age Input
        tk.Label(input_frame, text="Your Age:", bg='#1E2F3E', fg='white',
                font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        self.age_entry = ttk.Entry(input_frame, width=5)
        self.age_entry.pack(side=tk.LEFT, padx=5)
        
        # Food Input
        tk.Label(input_frame, text="Enter Food:", bg='#1E2F3E', fg='white',
                font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        self.food_entry = ttk.Entry(input_frame, width=30)
        self.food_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        ttk.Button(input_frame, text="Check Food",
                  command=self.analyze_food).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Get Age Recommendations",
                  command=self.show_age_recommendations).pack(side=tk.LEFT, padx=5)
        
        # Display Area
        self.display_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                    width=80, height=30,
                                                    bg='#2C3E50', fg='white',
                                                    font=("Arial", 11))
        self.display_area.pack(padx=10, pady=10)
        
        # Welcome Message
        welcome_text = """
🥗 Welcome to Personal Health Advisor!

This bot helps you:
• Check nutrition facts for foods
• Get age-specific dietary recommendations
• Learn about food benefits
• Make healthy food choices

Enter your age and food items to begin.
        """
        self.add_message(welcome_text)
        
    def add_message(self, message):
        self.display_area.insert(tk.END, message + "\n")
        self.display_area.see(tk.END)
        
    def analyze_food(self):
        food = self.food_entry.get().lower().strip()
        if not food:
            self.add_message("Please enter a food item!")
            return
            
        self.display_area.delete(1.0, tk.END)
        self.add_message(f"📊 Analyzing: {food.title()}\n")
        
        if food in self.food_data:
            data = self.food_data[food]
            self.add_message("=" * 40)
            self.add_message(f"Nutrition Facts for {food.title()}:")
            self.add_message(f"🔥 Calories: {data['calories']}")
            self.add_message(f"🥩 Protein: {data['protein']}")
            self.add_message(f"🍞 Carbs: {data['carbs']}")
            self.add_message(f"🥑 Fat: {data['fat']}")
            self.add_message(f"🍯 Sugar: {data['sugar']}")
            self.add_message("\n💪 Benefits:")
            for benefit in data['benefits']:
                self.add_message(f"• {benefit}")
            self.add_message("=" * 40)
        else:
            self.add_message("Food not found in database.")
            
    def show_age_recommendations(self):
        try:
            age = int(self.age_entry.get())
            self.display_area.delete(1.0, tk.END)
            
            if age <= 12:
                category = 'child'
            elif age <= 19:
                category = 'teen'
            elif age <= 60:
                category = 'adult'
            else:
                category = 'senior'
                
            recommendations = self.age_recommendations[category]
            
            self.add_message(f"🎯 Dietary Recommendations for Age {age} ({category.title()})\n")
            self.add_message("=" * 40)
            self.add_message(f"📈 Daily Calories: {recommendations['daily_calories']}")
            
            self.add_message("\n✅ Recommended Foods:")
            for food in recommendations['recommended']:
                self.add_message(f"• {food}")
                
            self.add_message("\n❌ Foods to Avoid:")
            for food in recommendations['avoid']:
                self.add_message(f"• {food}")
            self.add_message("=" * 40)
            
        except ValueError:
            self.add_message("Please enter a valid age!")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    bot = HealthAdvisorBot()
    bot.run()