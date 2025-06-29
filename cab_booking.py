from flask import Flask, render_template, request, jsonify, session
import folium
from folium.plugins import LocateControl, MousePosition
import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random
import sqlite3
from datetime import datetime
import hashlib
import openai
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database initialization
def init_db():
    conn = sqlite3.connect('cab_booking.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, 
                  password TEXT, role TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (id INTEGER PRIMARY KEY, name TEXT, vehicle_no TEXT, 
                  lat REAL, lon REAL, status TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY, user_id INTEGER, driver_id INTEGER,
                  pickup_lat REAL, pickup_lon REAL, 
                  drop_lat REAL, drop_lon REAL,
                  status TEXT, fare REAL, created_at TEXT)''')
    
    # Add sample drivers
    c.execute('INSERT OR IGNORE INTO drivers (name, vehicle_no, lat, lon, status) VALUES (?, ?, ?, ?, ?)',
             ('John Doe', 'KA01AB1234', 12.9716, 77.5946, 'available'))
             
    conn.commit()
    conn.close()

class CabBookingSystem:
    def __init__(self):
        self.map = None
        self.user_location = self.get_location()
        self.available_drivers = self.get_available_drivers()
        self.create_map()
    
    def get_location(self):
        try:
            ip = requests.get('https://api.ipify.org').text
            response = requests.get(f'https://ipapi.co/{ip}/json/').json()
            return {
                'lat': response.get('latitude', 12.9716),
                'lon': response.get('longitude', 77.5946),
                'address': response.get('city', '') + ', ' + response.get('country_name', '')
            }
        except:
            return {'lat': 12.9716, 'lon': 77.5946, 'address': 'Bangalore, India'}
    
    def get_available_drivers(self):
        conn = sqlite3.connect('cab_booking.db')
        c = conn.cursor()
        c.execute('SELECT * FROM drivers WHERE status = "available"')
        drivers = c.fetchall()
        conn.close()
        return drivers
    
    def create_map(self):
        self.map = folium.Map(
            location=[self.user_location['lat'], self.user_location['lon']],
            zoom_start=13
        )
        
        # Add user marker
        folium.Marker(
            [self.user_location['lat'], self.user_location['lon']],
            popup='Your Location',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.map)
        
        # Add driver markers
        for driver in self.available_drivers:
            driver_html = f"""
                <div style='min-width:200px'>
                    <b>Driver: {driver[1]}</b><br>
                    Vehicle: {driver[2]}<br>
                    <button onclick='bookDriver({driver[0]})' 
                            style='background:#4CAF50;color:white;padding:8px;
                                   border:none;border-radius:4px;margin-top:5px'>
                        Book Now
                    </button>
                </div>
            """
            folium.Marker(
                [driver[3], driver[4]],
                popup=driver_html,
                icon=folium.Icon(color='blue', icon='car', prefix='fa')
            ).add_to(self.map)
        
        # Add controls
        LocateControl().add_to(self.map)
        MousePosition().add_to(self.map)
        
        # Add booking interface
        self.map.get_root().html.add_child(folium.Element(self.create_booking_interface()))
        
        self.map.save('templates/map.html')
    
    def create_booking_interface(self):
        return """
        <div style='position:fixed;top:10px;right:10px;background:white;
                    padding:20px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);
                    z-index:1000;min-width:300px'>
            <h3>Book a Cab</h3>
            <div style='margin:10px 0'>
                <label>Pickup:</label>
                <input type='text' id='pickup' class='location-input'>
            </div>
            <div style='margin:10px 0'>
                <label>Destination:</label>
                <input type='text' id='destination' class='location-input'>
            </div>
            <div style='margin:10px 0'>
                <label>Cab Type:</label>
                <select id='cabType'>
                    <option value='mini'>Mini</option>
                    <option value='sedan'>Sedan</option>
                    <option value='suv'>SUV</option>
                </select>
            </div>
            <button onclick='searchCabs()' style='background:#4CAF50;color:white;
                                                 padding:10px;border:none;width:100%'>
                Search Cabs
            </button>
            <div id='fareEstimate'></div>
            <div id='chatbot' style='margin-top:20px'>
                <div style='border-top:1px solid #ddd;padding-top:10px'>
                    <h4>Need Help?</h4>
                    <input type='text' id='chatInput' placeholder='Ask me anything...'
                           style='width:100%;padding:5px;margin:5px 0'>
                    <button onclick='askChatbot()' style='background:#007bff;
                                                         color:white;padding:5px;
                                                         border:none;width:100%'>
                        Ask
                    </button>
                    <div id='chatResponse' style='margin-top:10px'></div>
                </div>
            </div>
        </div>
        <script>
        function searchCabs() {
            const pickup = document.getElementById('pickup').value;
            const destination = document.getElementById('destination').value;
            const cabType = document.getElementById('cabType').value;
            
            fetch('/search_cabs', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pickup, destination, cabType})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('fareEstimate').innerHTML = 
                    `Estimated fare: ₹${data.fare}`;
            });
        }
        
        function bookDriver(driverId) {
            fetch('/book_cab', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({driverId})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            });
        }
        
        function askChatbot() {
            const query = document.getElementById('chatInput').value;
            fetch('/chatbot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('chatResponse').innerHTML = data.response;
            });
        }
        </script>
        """

# Routes
@app.route('/')
def index():
    return render_template('map.html')

@app.route('/search_cabs', methods=['POST'])
def search_cabs():
    data = request.json
    # Calculate fare based on distance (simplified)
    base_fare = {'mini': 50, 'sedan': 80, 'suv': 100}
    fare = base_fare[data['cabType']] + random.randint(100, 300)
    return jsonify({'fare': fare})

@app.route('/book_cab', methods=['POST'])
def book_cab():
    driver_id = request.json['driverId']
    # Create booking record
    conn = sqlite3.connect('cab_booking.db')
    c = conn.cursor()
    c.execute('''INSERT INTO bookings 
                 (user_id, driver_id, status, created_at) 
                 VALUES (?, ?, ?, ?)''',
              (1, driver_id, 'confirmed', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking confirmed! Driver is on the way.'})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    query = request.json['query']
    # Simple response logic (can be replaced with OpenAI or other AI)
    responses = {
        'fare': 'Our fares start from ₹50 with additional per km charges.',
        'cancel': 'You can cancel your ride within 5 minutes of booking.',
        'payment': 'We accept cash, cards, and UPI payments.',
    }
    response = responses.get(
        query.lower().split()[0], 
        "I'm here to help! Please ask about fares, cancellation, or payments."
    )
    return jsonify({'response': response})

if __name__ == '__main__':
    # Create required directories
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Initialize database
    init_db()
    
    # Create map
    cab_system = CabBookingSystem()
    
    # Run app
    app.run(debug=True)