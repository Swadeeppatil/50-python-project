import speech_recognition as sr
import pyttsx3
import datetime
import re

class WeOfferAssistant:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Company information
        self.company_info = {
            "about": "WeOffer is a company specializing in providing customized digital solutions tailored to unique business requirements. We create one-of-a-kind digital experiences that improve online visibility and produce meaningful outcomes.",
            "services": [
                "Custom digital solutions",
                "Online visibility improvement",
                "Strategic technology integration",
                "Business goal achievement assistance",
                "Digital experience creation"
            ],
            "approach": "We assist businesses by reducing complicated challenges through the strategic integration of cutting-edge technology."
        }
    
    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"User: {text}")
            return text.lower()
        except:
            return ""
    
    def process_query(self, query):
        # About company
        if re.search(r'what.*(company|weoffer|business)|about.*company|company.*about|tell.*about', query):
            return self.company_info["about"]
        
        # Services
        elif re.search(r'what.*services|services.*provide|offer', query):
            services = "\n- ".join(self.company_info["services"])
            return f"We offer the following services:\n- {services}"
        
        # Approach
        elif re.search(r'how.*work|approach|methodology', query):
            return self.company_info["approach"]
        
        # Greetings
        elif re.search(r'hi|hello|hey', query):
            return "Hello! I'm WeOffer's virtual assistant. How can I help you today?"
        
        # Goodbye
        elif re.search(r'bye|goodbye|exit|quit', query):
            return "exit"
        
        # Default response
        return "I apologize, but I'm not sure about that. Would you like to know about our company, our services, or our approach to helping businesses?"
    
    def run(self):
        self.speak("Welcome to WeOffer! I'm your virtual assistant. How can I help you today?")
        
        while True:
            query = self.listen()
            
            if query:
                response = self.process_query(query)
                
                if response == "exit":
                    self.speak("Thank you for contacting WeOffer. Have a great day!")
                    break
                
                self.speak(response)

if __name__ == "__main__":
    assistant = WeOfferAssistant()
    assistant.run()