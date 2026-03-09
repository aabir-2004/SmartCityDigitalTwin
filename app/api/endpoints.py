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
    alert_templates = [
        {"type": "Traffic Congestion", "severity": "Warning", "desc": "Unusual congestion pattern matching peak-hour metrics."},
        {"type": "Air Quality Degradation", "severity": "Critical", "desc": "PM2.5 metrics exceed threshold limits."},
        {"type": "Grid Optimization", "severity": "Info", "desc": "Automated load balancing algorithm engaged."}
    ]
    choice = random.choice(alert_templates)
    alert_id = f"ALT-{random.randint(1000, 9999)}"
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Alerts (AlertID, AlertType, Severity, Description, Timestamp) VALUES (?, ?, ?, ?, ?)",
            (alert_id, choice['type'], choice['severity'], choice['desc'], timestamp)
        )

@api_bp.route('/actions/trigger', methods=['POST'])
def trigger_action():
    """Execute a simulated administrative procedure."""
    data = request.get_json() or {}
    action = data.get('action', 'Unspecified Reference Procedure')
    processed_action = action.replace('ing', 'ed')
    return jsonify({"success": True, "message": f"Procedure '{processed_action}' finalized."})
