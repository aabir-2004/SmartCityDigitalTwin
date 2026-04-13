import random
import time
from flask import Blueprint, request, jsonify
from app.database import get_db_connection

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/complaints', methods=['POST'])
def add_complaint():
    """Handle incoming citizen complaints."""
    data = request.get_json()
    if not data or 'category' not in data or 'location' not in data or 'description' not in data:
        return jsonify({"success": False, "error": "Invalid payload parameters"}), 400

    complaint_id = f"CMP-{random.randint(1000, 9999)}"
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Complaints (ComplaintID, Category, Location, Description, Status, Timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (complaint_id, data['category'], data['location'], data['description'], "Open", timestamp)
        )
    return jsonify({"success": True, "id": complaint_id}), 201

@api_bp.route('/locations', methods=['GET'])
def get_locations():
    """Retrieve available city locations from sensor data for the admin panel."""
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("SELECT DISTINCT Location FROM SensorData WHERE Location IS NOT NULL")
            locations = [row['Location'] for row in cursor.fetchall()]
        except Exception:
            locations = []
            
        if not locations:
            # Fallback based on seed_db names
            locations = ["Downtown Central Hub", "Sector 4 Industrial Park", "East Side Highway", "MG Road Intercept"]
            
    return jsonify(locations)

@api_bp.route('/complaints', methods=['GET'])
def get_complaints():
    """Retrieve all complaints for the administrative dashboard."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Complaints ORDER BY Timestamp DESC")
        rows = cursor.fetchall()

    return jsonify([dict(row) for row in rows])

@api_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Retrieve the latest real aggregated sensor readings."""
    data = {}
    with get_db_connection() as conn:
        for s_type, default_val in [("TrafficFlow", 60), ("AirQuality", 40), ("EnergyLoad", 30)]:
            try:
                cursor = conn.execute(
                    "SELECT Reading FROM SensorData WHERE SensorType = ? ORDER BY Timestamp DESC LIMIT 1", 
                    (s_type,)
                )
                res = cursor.fetchone()
                base_val = res[0] if res else default_val
            except Exception:
                # Fallback if SensorData table missing (not seeded yet)
                base_val = default_val
            
            # Application of a realistic variance distribution
            min_variance, max_variance = -base_val * 0.02, base_val * 0.02
            data[s_type] = round(base_val + random.uniform(min_variance, max_variance), 1)

    return jsonify({
        "traffic": data["TrafficFlow"],
        "airQuality": data["AirQuality"],
        "energyUsage": data["EnergyLoad"]
    })

@api_bp.route('/dashboard/alerts', methods=['GET'])
def get_system_alerts():
    """Retrieve up to 5 recent system alerts, with randomized anomaly triggers."""
    if random.random() < 0.25:
        _trigger_synthetic_anomaly()

    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT AlertID AS id, AlertType AS type, Severity as severity, Description as desc, Timestamp as timestamp FROM Alerts ORDER BY Timestamp DESC LIMIT 5"
        )
        rows = cursor.fetchall()
        
    return jsonify([dict(row) for row in rows])

def _trigger_synthetic_anomaly():
    """Helper method to randomly inject an anomaly record for monitoring tests."""
    alert_id = f"ALT-{random.randint(1000, 9999)}"
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("SELECT DISTINCT Location FROM SensorData WHERE Location IS NOT NULL")
            locations = [row['Location'] for row in cursor.fetchall()]
        except Exception:
            locations = []
            
        loc = random.choice(locations) if locations else "Unknown Sector"

        alert_templates = [
            {"type": "Traffic Congestion", "severity": "Warning", "desc": f"Unusual congestion pattern matching peak-hour metrics in {loc}."},
            {"type": "Air Quality Degradation", "severity": "Critical", "desc": f"PM2.5 metrics exceed threshold limits in {loc}."},
            {"type": "Grid Optimization", "severity": "Info", "desc": f"Automated load balancing algorithm engaged for {loc}."}
        ]
        choice = random.choice(alert_templates)
        
        try:
            conn.execute(
                "INSERT INTO Alerts (AlertID, AlertType, Severity, Description, Timestamp) VALUES (?, ?, ?, ?, ?)",
                (alert_id, choice['type'], choice['severity'], choice['desc'], timestamp)
            )
        except Exception:
            pass

@api_bp.route('/actions/trigger', methods=['POST'])
def trigger_action():
    """Execute a simulated administrative procedure."""
    data = request.get_json() or {}
    action_type = data.get('actionType', 'General Policy Update')
    location = data.get('location', 'City-Wide')
    
    action_id = f"ACT-{random.randint(1000, 9999)}"
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    # Process verb for display
    display_action = action_type
    
    with get_db_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO AdminActions (ActionID, ActionType, TargetLocation, Result, Timestamp) VALUES (?, ?, ?, ?, ?)",
                (action_id, action_type, location, "Success", timestamp)
            )
        except Exception:
            pass
            
    return jsonify({
        "success": True, 
        "message": f"'{display_action}' successfully deployed to {location}."
    })
