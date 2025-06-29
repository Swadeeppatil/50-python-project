import folium
from flask import Flask, render_template
import requests
import json
from geopy.geocoders import Nominatim
import webbrowser
from folium.plugins import LocateControl, MousePosition
from folium.features import CustomIcon
import socket

app = Flask(__name__)

class LocationMap:
    def __init__(self):
        self.map = None
        self.user_location = self.get_location()
        self.create_map()
        
    def get_location(self):
        try:
            # Get IP-based location
            ip = requests.get('https://api.ipify.org').text
            response = requests.get(f'https://ipapi.co/{ip}/json/').json()
            return {
                'lat': response.get('latitude', 0),
                'lon': response.get('longitude', 0),
                'city': response.get('city', 'Unknown'),
                'country': response.get('country_name', 'Unknown')
            }
        except:
            # Default location (New York)
            return {'lat': 40.7128, 'lon': -74.0060, 'city': 'New York', 'country': 'USA'}

    def create_map(self):
        # Create base map centered on user location
        self.map = folium.Map(
            location=[self.user_location['lat'], self.user_location['lon']],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add tile layers with proper attribution
        folium.TileLayer(
            'Stamen Terrain',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
        ).add_to(self.map)
        
        folium.TileLayer(
            'Stamen Toner',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
        ).add_to(self.map)
        
        folium.TileLayer(
            'CartoDB dark_matter',
            attr='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="http://cartodb.com/attributions">CartoDB</a>'
        ).add_to(self.map)
        
        # Add location marker
        folium.Marker(
            [self.user_location['lat'], self.user_location['lon']],
            popup=f"You are here!<br>City: {self.user_location['city']}<br>Country: {self.user_location['country']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.map)
        
        # Add circle around location
        folium.Circle(
            radius=1000,
            location=[self.user_location['lat'], self.user_location['lon']],
            popup='1km radius',
            color='red',
            fill=True
        ).add_to(self.map)
        
        # Add location control
        LocateControl(
            auto_start=True,
            position='topleft'
        ).add_to(self.map)
        
        # Add mouse position
        MousePosition().add_to(self.map)
        
        # Add layer control
        folium.LayerControl().add_to(self.map)
        
        # Save map
        self.map.save('templates/map.html')

@app.route('/')
def show_map():
    return render_template('map.html')

def create_search_box():
    search_html = """
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.5);">
        <input type="text" id="search" placeholder="Search location..." style="padding: 5px;">
        <button onclick="searchLocation()" style="padding: 5px;">Search</button>
    </div>
    <script>
    function searchLocation() {
        var location = document.getElementById('search').value;
        fetch('/search?q=' + encodeURIComponent(location))
            .then(response => response.json())
            .then(data => {
                map.setView([data.lat, data.lon], 13);
            });
    }
    </script>
    """
    return search_html

@app.route('/search')
def search():
    query = request.args.get('q', '')
    geolocator = Nominatim(user_agent="my_map_app")
    try:
        location = geolocator.geocode(query)
        return jsonify({'lat': location.latitude, 'lon': location.longitude})
    except:
        return jsonify({'error': 'Location not found'})

if __name__ == '__main__':
    # Create map
    location_map = LocationMap()
    
    # Add search box to map
    location_map.map.get_root().html.add_child(folium.Element(create_search_box()))
    location_map.map.save('templates/map.html')
    
    # Create required directories
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run Flask app
    app.run(debug=True)