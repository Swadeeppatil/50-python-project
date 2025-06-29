import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
import requests
import json
import os
from opencage.geocoder import OpenCageGeocode
from PIL import Image, ImageTk
import webbrowser

class PhoneTracker:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Phone Number Location Tracker")
        self.window.geometry("800x600")
        self.window.configure(bg='#2C3E50')
        
        # OpenCage API Key - Replace with your key
        self.api_key = 'YOUR_OPENCAGE_API_KEY'
        self.geocoder = OpenCageGeocode(self.api_key)
        
        self.create_gui()
        
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(expand=True, fill='both')
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Phone Number Details", padding="10")
        input_frame.pack(fill='x', pady=10)
        
        ttk.Label(input_frame, text="Enter Phone Number (with country code):").pack()
        self.phone_entry = ttk.Entry(input_frame, width=40)
        self.phone_entry.pack(pady=5)
        self.phone_entry.insert(0, "+91")  # Default country code
        
        ttk.Button(input_frame, text="Track Location",
                  command=self.track_number).pack(pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        # Basic info
        info_frame = ttk.Frame(results_frame)
        info_frame.pack(fill='x', pady=5)
        
        # Country
        ttk.Label(info_frame, text="Country:").grid(row=0, column=0, sticky='w', padx=5)
        self.country_label = ttk.Label(info_frame, text="-")
        self.country_label.grid(row=0, column=1, sticky='w', padx=5)
        
        # Region
        ttk.Label(info_frame, text="Region:").grid(row=1, column=0, sticky='w', padx=5)
        self.region_label = ttk.Label(info_frame, text="-")
        self.region_label.grid(row=1, column=1, sticky='w', padx=5)
        
        # Carrier
        ttk.Label(info_frame, text="Carrier:").grid(row=2, column=0, sticky='w', padx=5)
        self.carrier_label = ttk.Label(info_frame, text="-")
        self.carrier_label.grid(row=2, column=1, sticky='w', padx=5)
        
        # Timezone
        ttk.Label(info_frame, text="Timezone:").grid(row=3, column=0, sticky='w', padx=5)
        self.timezone_label = ttk.Label(info_frame, text="-")
        self.timezone_label.grid(row=3, column=1, sticky='w', padx=5)
        
        # Map frame
        self.map_frame = ttk.LabelFrame(results_frame, text="Location Map", padding="10")
        self.map_frame.pack(fill='both', expand=True, pady=10)
        
        # Create a text widget for additional details
        self.details_text = scrolledtext.ScrolledText(results_frame, height=5)
        self.details_text.pack(fill='x', pady=5)
        
    def track_number(self):
        phone_number = self.phone_entry.get()
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone_number)
            
            # Get country
            country = geocoder.description_for_number(parsed_number, "en")
            self.country_label.config(text=country)
            
            # Get carrier
            service_provider = carrier.name_for_number(parsed_number, "en")
            self.carrier_label.config(text=service_provider)
            
            # Get timezone
            time_zone = timezone.time_zones_for_number(parsed_number)
            self.timezone_label.config(text=str(time_zone[0]) if time_zone else "-")
            
            # Get region/location using OpenCage Geocoder
            query = country
            results = self.geocoder.geocode(query)
            
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                region = results[0]['components'].get('state', '-')
                self.region_label.config(text=region)
                
                # Create map
                location_map = folium.Map(location=[lat, lng], zoom_start=6)
                folium.Marker([lat, lng], popup=country).add_to(location_map)
                
                # Save map
                map_file = "phone_location_map.html"
                location_map.save(map_file)
                
                # Open map in default browser
                webbrowser.open(map_file)
                
                # Update details
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, 
                    f"Detailed Information:\n"
                    f"Country Code: {parsed_number.country_code}\n"
                    f"National Number: {parsed_number.national_number}\n"
                    f"Latitude: {lat}\n"
                    f"Longitude: {lng}\n"
                    f"Location: {results[0]['formatted']}"
                )
                
            else:
                messagebox.showerror("Error", "Could not determine exact location")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PhoneTracker()
    app.run()