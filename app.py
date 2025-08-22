from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from datetime import datetime, timedelta
import random
import json
import threading
import time

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'citypulse-hackathon-secret-2024'
app.config['UPLOAD_FOLDER'] = '../uploads'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory database simulation (replace with real DB in production)
class CityPulseDB:
    def __init__(self):
        self.users = {}
        self.reports = []
        self.projects = []
        self.alerts = []
        self.infrastructure = []
        self.satellite_data = []
        self.init_demo_data()
    
    def init_demo_data(self):
        # Demo users
        self.users = {
            'admin': {'id': 1, 'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@citypulse.com'},
            'johndoe': {'id': 2, 'username': 'johndoe', 'password': 'password123', 'role': 'citizen', 'email': 'john@example.com', 'credits': 245, 'reports_submitted': 12, 'reports_resolved': 8},
            'sarahj': {'id': 3, 'username': 'sarahj', 'password': 'password123', 'role': 'citizen', 'email': 'sarah@example.com', 'credits': 420, 'reports_submitted': 28, 'reports_resolved': 15},
        }
        
        # Demo infrastructure projects
        self.projects = [
            {
                'id': 1, 'name': 'Highway 101 Expansion', 'type': 'road', 'status': 'in_progress', 
                'progress': 75, 'budget': '$45M', 'timeline': 'Jan 2024 - Dec 2024',
                'contractor': 'ABC Construction', 'description': 'Widening highway to 6 lanes',
                'latitude': 37.7749, 'longitude': -122.4194, 'impact_level': 'high'
            },
            {
                'id': 2, 'name': 'Central Park Renovation', 'type': 'public_space', 'status': 'in_progress', 
                'progress': 45, 'budget': '$12M', 'timeline': 'Mar 2024 - Nov 2024',
                'contractor': 'Green Spaces Inc', 'description': 'Complete park renovation with new facilities',
                'latitude': 37.7690, 'longitude': -122.4140, 'impact_level': 'medium'
            }
        ]
        
        # Demo infrastructure data
        self.infrastructure = [
            {'id': 1, 'type': 'road', 'name': 'Main Street', 'condition': 'good', 'last_inspection': '2024-01-15', 'latitude': 37.7750, 'longitude': -122.4180},
            {'id': 2, 'type': 'bridge', 'name': 'Downtown Bridge', 'condition': 'fair', 'last_inspection': '2023-11-20', 'latitude': 37.7760, 'longitude': -122.4170},
            {'id': 3, 'type': 'power_grid', 'name': 'North District Grid', 'condition': 'excellent', 'last_inspection': '2024-02-01', 'latitude': 37.7780, 'longitude': -122.4150}
        ]
        
        # Demo satellite data (urban growth metrics)
        self.satellite_data = [
            {'year': 2020, 'built_up_area': 45.2, 'green_space': 32.1, 'population_density': 4200},
            {'year': 2021, 'built_up_area': 46.8, 'green_space': 31.5, 'population_density': 4320},
            {'year': 2022, 'built_up_area': 48.3, 'green_space': 30.8, 'population_density': 4450},
            {'year': 2023, 'built_up_area': 50.1, 'green_space': 29.9, 'population_density': 4610},
            {'year': 2024, 'built_up_area': 52.7, 'green_space': 28.7, 'population_density': 4780}
        ]

# Initialize database
db = CityPulseDB()

# Simulated external services
class SatelliteService:
    def get_urban_growth_data(self, latitude, longitude, radius_km=10):
        """Simulate satellite data analysis for urban growth"""
        return {
            'built_up_area': random.uniform(40, 60),
            'green_space': random.uniform(25, 35),
            'population_density': random.randint(3000, 5000),
            'growth_rate': random.uniform(2.5, 5.5),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def detect_infrastructure_changes(self, latitude, longitude):
        """Simulate change detection from satellite imagery"""
        changes = []
        if random.random() > 0.7:
            changes.append({
                'type': 'new_construction',
                'confidence': random.uniform(0.7, 0.95),
                'area': random.uniform(500, 5000),
                'detected_date': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        return changes

class GovernmentAPIService:
    def get_planned_projects(self, area_code):
        """Simulate government API for planned infrastructure projects"""
        return [
            {
                'name': 'Smart City Initiative Phase 2',
                'type': 'digital_infrastructure',
                'budget': '$30M',
                'timeline': '2024-2026',
                'status': 'planned'
            },
            {
                'name': 'Public Transit Expansion',
                'type': 'transportation',
                'budget': '$120M', 
                'timeline': '2025-2027',
                'status': 'proposed'
            }
        ]
    
    def get_regulations(self, project_type):
        """Simulate building regulations and compliance data"""
        return {
            'zoning_restrictions': ['height_limit_50m', 'setback_10m'],
            'environmental_requirements': ['green_building_cert', 'stormwater_management'],
            'permit_requirements': ['building_permit', 'environmental_impact_assessment']
        }

# Initialize services
satellite_service = SatelliteService()
government_service = GovernmentAPIService()

# Real-time alert system
class AlertSystem:
    def __init__(self):
        self.active_alerts = []
        self.subscribers = set()
    
    def add_alert(self, alert_type, severity, area, description, coordinates=None):
        alert = {
            'id': len(self.active_alerts) + 1,
            'type': alert_type,
            'severity': severity,
            'area': area,
            'description': description,
            'coordinates': coordinates,
            'timestamp': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=6)).isoformat()
        }
        self.active_alerts.append(alert)
        
        # Broadcast to all connected clients
        socketio.emit('new_alert', alert)
        return alert
    
    def get_active_alerts(self):
        return [alert for alert in self.active_alerts 
                if datetime.fromisoformat(alert['expires_at']) > datetime.utcnow()]

alert_system = AlertSystem()

# Authentication middleware
def require_auth(role=None):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Simple token validation (in real app, use JWT)
            username = token[7:]  # Remove 'Bearer ' prefix
            user = db.users.get(username)
            
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            
            if role and user['role'] != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(user, *args, **kwargs)
        return decorated_function
    return decorator

# API Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = db.users.get(username)
    if user and user['password'] == password:
        # Simple token (use JWT in production)
        return jsonify({
            'success': True,
            'token': f'Bearer {username}',
            'user': {k: v for k, v in user.items() if k != 'password'}
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/urban-growth', methods=['GET'])
def get_urban_growth_data():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if not lat or not lng:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    data = satellite_service.get_urban_growth_data(lat, lng)
    return jsonify(data)

@app.route('/api/infrastructure-projects', methods=['GET'])
def get_infrastructure_projects():
    project_type = request.args.get('type')
    
    if project_type:
        projects = [p for p in db.projects if p['type'] == project_type]
    else:
        projects = db.projects
    
    return jsonify(projects)

@app.route('/api/infrastructure-status', methods=['GET'])
def get_infrastructure_status():
    return jsonify(db.infrastructure)

@app.route('/api/reports', methods=['GET', 'POST'])
@require_auth()
def handle_reports(user):
    if request.method == 'GET':
        # Return reports based on user role
        if user['role'] == 'admin':
            reports = db.reports
        else:
            reports = [r for r in db.reports if r['user_id'] == user['id']]
        
        return jsonify(reports)
    
    else:  # POST
        data = request.get_json()
        report = {
            'id': len(db.reports) + 1,
            'user_id': user['id'],
            'type': data['type'],
            'description': data['description'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'status': 'pending',
            'priority': data.get('priority', 'medium'),
            'created_at': datetime.utcnow().isoformat(),
            'image_url': data.get('image_url')
        }
        
        db.reports.append(report)
        
        # If it's a high-priority issue, create an alert
        if data.get('priority') == 'high':
            alert_system.add_alert(
                alert_type=data['type'],
                severity='high',
                area='Multiple districts',
                description=f'New high-priority issue: {data["description"]}',
                coordinates={'lat': data['latitude'], 'lng': data['longitude']}
            )
        
        # Update user credits if citizen
        if user['role'] == 'citizen':
            user['reports_submitted'] = user.get('reports_submitted', 0) + 1
            user['credits'] = user.get('credits', 0) + 20
        
        return jsonify({'success': True, 'report': report, 'credits': user.get('credits', 0)})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify(alert_system.get_active_alerts())

@app.route('/api/bottlenecks', methods=['GET'])
def get_bottlenecks():
    # Simulate bottleneck analysis
    bottlenecks = [
        {
            'id': 1,
            'type': 'traffic',
            'location': 'Main St & 5th Ave',
            'severity': 'high',
            'duration': '2+ hours daily',
            'impact': '15-20 min delays'
        },
        {
            'id': 2,
            'type': 'construction',
            'location': 'Highway 101 Northbound',
            'severity': 'medium', 
            'duration': '3 months',
            'impact': 'Lane closures during rush hour'
        }
    ]
    return jsonify(bottlenecks)

@app.route('/api/analytics/urban-growth', methods=['GET'])
def get_urban_growth_analytics():
    return jsonify(db.satellite_data)

@app.route('/api/analytics/infrastructure-health', methods=['GET'])
def get_infrastructure_health():
    # Simulate infrastructure health metrics
    return jsonify({
        'road_condition': {'excellent': 45, 'good': 35, 'fair': 15, 'poor': 5},
        'bridge_condition': {'excellent': 30, 'good': 40, 'fair': 20, 'poor': 10},
        'public_transit_score': 78,
        'overall_infrastructure_grade': 'B'
    })

@app.route('/api/government/projects', methods=['GET'])
def get_government_projects():
    area_code = request.args.get('area_code', 'default')
    return jsonify(government_service.get_planned_projects(area_code))

@app.route('/api/government/regulations', methods=['GET'])
def get_regulations():
    project_type = request.args.get('project_type')
    return jsonify(government_service.get_regulations(project_type))

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to CityPulse real-time updates'})

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts(data):
    alert_system.subscribers.add(request.sid)
    emit('alerts_update', alert_system.get_active_alerts())

@socketio.on('disconnect')
def handle_disconnect():
    alert_system.subscribers.discard(request.sid)
    print('Client disconnected')

# Background task for simulated real-time updates
def background_task():
    """Simulate real-time urban data updates"""
    while True:
        time.sleep(30)  # Update every 30 seconds
        
        # Simulate random alerts
        if random.random() > 0.7:
            alert_types = ['traffic', 'power_outage', 'water_main', 'road_closure']
            areas = ['Downtown', 'North District', 'South District', 'East Side']
            
            alert_system.add_alert(
                alert_type=random.choice(alert_types),
                severity=random.choice(['low', 'medium', 'high']),
                area=random.choice(areas),
                description=f'Simulated alert for testing purposes'
            )
        
        # Broadcast infrastructure updates
        socketio.emit('infrastructure_update', {
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Infrastructure data updated'
        })

# Start background thread
threading.Thread(target=background_task, daemon=True).start()

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory('../frontend', path)

# Add these imports to your app.py
import requests
from math import radians, sin, cos, sqrt, atan2

# OpenStreetMap/Nominatim geocoding service
def geocode_address_nominatim(address):
    """Geocode using OpenStreetMap's Nominatim service"""
    try:
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon']),
                'place_name': data[0]['display_name']
            }
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def reverse_geocode_nominatim(lat, lng):
    """Reverse geocode using OpenStreetMap's Nominatim service"""
    try:
        url = 'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': lat,
            'lon': lng,
            'format': 'json'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data and 'display_name' in data:
            return {
                'address': data['display_name'],
                'coordinates': [lat, lng]
            }
        return {'coordinates': [lat, lng], 'address': 'Address not available'}
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return {'coordinates': [lat, lng], 'address': 'Error getting address'}

# Update your API routes to use OpenStreetMap
@app.route('/api/map/geocode', methods=['GET'])
def geocode_address():
    """Convert address to coordinates using OpenStreetMap"""
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address parameter required'}), 400
    
    result = geocode_address_nominatim(address)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Address not found'}), 404

@app.route('/api/map/reverse-geocode', methods=['GET'])
def reverse_geocode():
    """Convert coordinates to address using OpenStreetMap"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if not lat or not lng:
        return jsonify({'error': 'Latitude and longitude parameters required'}), 400
    
    result = reverse_geocode_nominatim(lat, lng)
    return jsonify(result)

@app.route('/api/map/config', methods=['GET'])
def get_map_config():
    """Return map configuration for OpenStreetMap"""
    return jsonify({
        'tile_layer': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        'default_center': [37.7749, -122.4194],  # San Francisco
        'default_zoom': 12
    })

if __name__ == '__main__':
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("🚀 CityPulse Backend Server Starting...")
    print("📍 http://localhost:1501")
    print("📡 WebSocket support enabled")
    print("🛰️ Satellite data integration ready")
    print("🏗️ Government API simulation active")
    print("🚨 Real-time alert system running")
    
    socketio.run(app, debug=True, port=1501, host='0.0.0.0')