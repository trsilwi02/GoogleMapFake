from flask import Flask, render_template, request, jsonify, send_from_directory
import folium
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from Algorithm import AStar
import os

app = Flask(__name__, static_folder='templates')

# Initialize the graph and coordinates
def initialize_map(place="Hanoi, Vietnam"):
    G = ox.graph_from_place(place, network_type='drive')
    coordinates = {node: (data['y'], data['x']) for node, data in G.nodes(data=True)}
    return G, coordinates

# Create initial map
def create_map(center_lat=21.0285, center_lon=105.8542):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    return m

@app.route('/')
def index():
    m = create_map()
    m.save('templates/map.html')
    return render_template('index.html')

@app.route('/map.html')
def serve_map():
    return send_from_directory('templates', 'map.html')

@app.route('/search', methods=['POST'])
def search():
    start_place = request.form.get('start')
    end_place = request.form.get('end')
    
    # Geocode the places
    geolocator = Nominatim(user_agent="my_agent")
    start_location = geolocator.geocode(start_place)
    end_location = geolocator.geocode(end_place)
    
    if not start_location or not end_location:
        return jsonify({'error': 'Could not find one or both locations'})
    
    # Initialize map and graph
    G, coordinates = initialize_map()
    
    # Find nearest nodes
    start_node = ox.nearest_nodes(G, start_location.longitude, start_location.latitude)
    end_node = ox.nearest_nodes(G, end_location.longitude, end_location.latitude)
    
    # Run A* algorithm
    astar = AStar(G, coordinates)
    path, cost = astar.find_path(start_node, end_node)
    
    if path is None:
        return jsonify({'error': 'No path found'})
    
    # Create map with route
    m = create_map(start_location.latitude, start_location.longitude)
    
    # Add markers
    folium.Marker([start_location.latitude, start_location.longitude], 
                 popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([end_location.latitude, end_location.longitude], 
                 popup='End', icon=folium.Icon(color='red')).add_to(m)
    
    # Add route
    route_coords = [(coordinates[node][0], coordinates[node][1]) for node in path]
    folium.PolyLine(route_coords, weight=2, color='blue', opacity=0.8).add_to(m)
    
    m.save('templates/map.html')
    return jsonify({'success': True})

if __name__ == '__main__':
    # Ensure templates directory exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True) 