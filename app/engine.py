import time
import random
from app.database import get_db_connection

SYSTEM_STATE = {
    "traffic": 60.0,
    "airQuality": 40.0,
    "energyUsage": 30.0,
    "traffic_trend": 0.5, 
    "airQuality_trend": 0.2,
    "energyUsage_trend": 0.1, 
}

NYC_ZONING_MAP = {
    "Downtown Central Hub": [40.7580, -73.9855],
    "Sector 4 Industrial Park": [40.7022, -73.9739],
    "Northside Residential": [40.7870, -73.9754],
    "East Side Highway": [40.7225, -73.9734],
    "MG Road Intercept": [40.7188, -74.0016],
    "Airport Express Link": [40.7716, -73.8744],
    "Green Valley Suburb": [40.6602, -73.9690],
    "City Hospital Junction": [40.7903, -73.9525],
    "Tech Park Avenue": [40.7411, -73.9897],
    "Riverfront Promenade": [40.7116, -74.0163],
    "Financial District": [40.7075, -74.0113],
    "Old Town Square": [40.7308, -73.9973]
}

SAFE_LAND_POINTS = [
    [40.7282, -73.9942], [40.7356, -74.0012], [40.6925, -73.9904],
    [40.8093, -73.9485], [40.7614, -73.9776], [40.8296, -73.9262]
]

def get_location_coordinates(location_name):
    if location_name in NYC_ZONING_MAP:
        return NYC_ZONING_MAP[location_name]
    hash_val = sum(ord(c) for c in location_name)
    return SAFE_LAND_POINTS[hash_val % len(SAFE_LAND_POINTS)]

DEPLOYED_RESOURCES = []

# Generate baseline resources
for _ in range(50):
    lat = 40.7128 + random.uniform(-0.06, 0.06)
    lng = -74.0060 + random.uniform(-0.06, 0.06)
    rtype = random.choice(['police', 'fire', 'environment', 'ambulance'])
    DEPLOYED_RESOURCES.append({
        "type": rtype, "lat": lat, "lng": lng, 
        "intensity": random.uniform(0.3, 0.7),
        "expires_at": time.time() + 600
    })

def apply_admin_action(action_type, location="City-Wide"):
    """
    Causal Feedback: Admin actions physically modify the persistent system state.
    """
    global SYSTEM_STATE
    
    action_type_lower = action_type.lower()
    
    if "traffic" in action_type_lower or "reroute" in action_type_lower:
        SYSTEM_STATE["traffic"] = max(10, SYSTEM_STATE["traffic"] - 25.0)
        SYSTEM_STATE["traffic_trend"] = -0.5  # Temporary relief
    elif "grid" in action_type_lower or "energy" in action_type_lower or "load" in action_type_lower:
        SYSTEM_STATE["energyUsage"] = max(10, SYSTEM_STATE["energyUsage"] - 15.0)
        SYSTEM_STATE["energyUsage_trend"] = -0.2
    elif "air" in action_type_lower or "pollution" in action_type_lower or "emission" in action_type_lower:
        SYSTEM_STATE["airQuality"] = max(10, SYSTEM_STATE["airQuality"] - 20.0)
        SYSTEM_STATE["airQuality_trend"] = -0.3
    else:
        # General systematic improvements
        SYSTEM_STATE["traffic"] *= 0.90
        SYSTEM_STATE["airQuality"] *= 0.90
        SYSTEM_STATE["energyUsage"] *= 0.90

    # Resource Allocation logic based on action
    if location != "City-Wide":
        coords = get_location_coordinates(location)
    else:
        coords = [40.7128 + random.uniform(-0.05, 0.05), -74.0060 + random.uniform(-0.05, 0.05)]

    lat, lng = coords[0], coords[1]
    
    # Deploy multiple units around the target location for heatmap visibility
    spawn_count = 15
    deployed_type = 'police'
    
    if "fire" in action_type_lower or "emergency" in action_type_lower or "rescue" in action_type_lower:
        deployed_type = 'fire'
    elif "air" in action_type_lower or "pollution" in action_type_lower or "purifier" in action_type_lower:
        deployed_type = 'environment'
    elif "ambulance" in action_type_lower or "medical" in action_type_lower:
        deployed_type = 'ambulance'
    elif "police" in action_type_lower or "authority" in action_type_lower or "army" in action_type_lower:
        deployed_type = 'police'

    # Check for complaints logic and provide feedback
    feedback = ""
    try:
        from app import socketio
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM Complaints WHERE Location = ? AND Status = 'Open'", (location,))
            complaints = cursor.fetchall()
            
            if not complaints and location != "City-Wide":
                feedback = f"Unit Feedback ({deployed_type.capitalize()}): Sector is clear. No anomalies detected."
            elif complaints:
                matched = False
                for c in complaints:
                    cat = c['Category'].lower()
                    desc = c['Description'].lower()
                    
                    is_match = False
                    if deployed_type == 'police' and ('traffic' in cat or 'security' in cat or 'crime' in desc):
                        is_match = True
                    elif deployed_type == 'fire' and ('fire' in cat or 'infrastructure' in cat or 'hazard' in desc):
                        is_match = True
                    elif deployed_type == 'ambulance' and ('health' in cat or 'accident' in cat or 'medical' in desc):
                        is_match = True
                    elif deployed_type == 'environment' and ('pollution' in cat or 'environment' in cat or 'air' in desc):
                        is_match = True
                    
                    if 'army' in action_type_lower or 'rescue squad' in action_type_lower:
                        is_match = True
                        
                    if is_match:
                        matched = True
                        conn.execute("UPDATE Complaints SET Status = 'Resolved' WHERE ComplaintID = ?", (c['ComplaintID'],))
                        socketio.emit('new_complaint', {"id": c['ComplaintID']})
                        
                if matched:
                    feedback = f"Unit Feedback ({deployed_type.capitalize()}): Problem resolved."
                    SYSTEM_STATE['traffic'] = max(10, SYSTEM_STATE['traffic'] * 0.4)
                    SYSTEM_STATE['airQuality'] = max(10, SYSTEM_STATE['airQuality'] * 0.4)
                    SYSTEM_STATE['energyUsage'] = max(10, SYSTEM_STATE['energyUsage'] * 0.4)
                else:
                    feedback = f"Unit Feedback ({deployed_type.capitalize()}): We need reinforcements! Incorrect department dispatched for current anomaly."

        if feedback:
            alert_id = f"ALT-{random.randint(1000, 9999)}"
            timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            try:
                with get_db_connection() as conn:
                    conn.execute("INSERT INTO Alerts (AlertID, AlertType, Severity, Description, Timestamp) VALUES (?, ?, ?, ?, ?)", 
                                 (alert_id, "Resource Feedback", "Info", feedback, timestamp))
            except Exception:
                pass
            socketio.emit('new_alert', {
                "id": alert_id, "type": "Resource Feedback", "severity": "Info", "desc": feedback
            })
    except Exception as e:
        pass

    for _ in range(spawn_count):
        dl_lat = lat + random.uniform(-0.015, 0.015)
        dl_lng = lng + random.uniform(-0.015, 0.015)
        DEPLOYED_RESOURCES.append({
            "type": deployed_type,
            "lat": dl_lat,
            "lng": dl_lng,
            "intensity": random.uniform(0.6, 1.0),
            "expires_at": time.time() + 600 # 10 minutes expiry
        })

    # Optional: trigger a websocket signal here if we want immediate map redrawing without poll,
    # but currently frontend uses toggleHeatmap/loadHeatmap flow. We can emit an event.
    try:
        from app import socketio
        socketio.emit('heatmap_refresh_required', {})
    except Exception:
        pass

    return feedback

def get_current_stats():
    return {
        "traffic": round(SYSTEM_STATE["traffic"], 1),
        "airQuality": round(SYSTEM_STATE["airQuality"], 1),
        "energyUsage": round(SYSTEM_STATE["energyUsage"], 1)
    }

def trigger_synthetic_anomaly(socketio):
    """Helper method to randomly inject an anomaly record and emit to clients."""
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
        
        # Only inject extreme alerts rarely, usually via loop
        if random.random() < 0.05:
             alert_templates.append({"type": "System Cascade Failure", "severity": "Extreme", "desc": f"Multiple infrastructure failures detected. Immediate Mayor attention required in {loc}!"})

        choice = random.choice(alert_templates)
        
        try:
            conn.execute(
                "INSERT INTO Alerts (AlertID, AlertType, Severity, Description, Timestamp) VALUES (?, ?, ?, ?, ?)",
                (alert_id, choice['type'], choice['severity'], choice['desc'], timestamp)
            )
        except Exception:
            pass
    
    # Broadcast Alert via WebSocket to map and dashboard
    socketio.emit('new_alert', {
        "id": alert_id, "type": choice['type'], 
        "severity": choice['severity'], "desc": choice['desc']
    })

def run_simulation_loop(socketio):
    """
    Background Task: Continuous time-evolving deterministic simulation.
    Drift + Trend + Noise mechanism influencing metrics every tick.
    """
    global SYSTEM_STATE
    global DEPLOYED_RESOURCES
    while True:
        socketio.sleep(2.5) # Non-blocking sleep for WebSocket async loop
        
        # Clean expired resources
        current_time = time.time()
        initial_len = len(DEPLOYED_RESOURCES)
        DEPLOYED_RESOURCES = [r for r in DEPLOYED_RESOURCES if r.get('expires_at', current_time + 100) > current_time]
        if len(DEPLOYED_RESOURCES) < initial_len:
            socketio.emit('heatmap_refresh_required', {})
        
        # 15% chance per tick to generate an anomaly 
        if random.random() < 0.15:
            trigger_synthetic_anomaly(socketio)
            
        # Traffic drift + noise
        noise_t = random.uniform(-1.0, 1.0)
        SYSTEM_STATE["traffic"] += SYSTEM_STATE["traffic_trend"] + noise_t
        
        # Reversion to mean mechanics or rubber-banding
        if SYSTEM_STATE["traffic"] > 95: SYSTEM_STATE["traffic_trend"] = -0.5
        elif SYSTEM_STATE["traffic"] < 30: SYSTEM_STATE["traffic_trend"] = 0.5
        
        # Air Quality causal effect (heavy traffic causes higher pollution delay)
        noise_a = random.uniform(-0.5, 0.5)
        if SYSTEM_STATE["traffic"] > 80:
            SYSTEM_STATE["airQuality"] += 0.8  # Direct correlation
        SYSTEM_STATE["airQuality"] += SYSTEM_STATE["airQuality_trend"] + noise_a
        
        if SYSTEM_STATE["airQuality"] > 90: SYSTEM_STATE["airQuality_trend"] = -0.3
        elif SYSTEM_STATE["airQuality"] < 20: SYSTEM_STATE["airQuality_trend"] = 0.2

        # Energy Load drift
        noise_e = random.uniform(-0.5, 0.5)
        SYSTEM_STATE["energyUsage"] += SYSTEM_STATE["energyUsage_trend"] + noise_e
        if SYSTEM_STATE["energyUsage"] > 85: SYSTEM_STATE["energyUsage_trend"] = -0.4
        elif SYSTEM_STATE["energyUsage"] < 20: SYSTEM_STATE["energyUsage_trend"] = 0.2

        # Extreme Alert Generation based on thresholds
        if (SYSTEM_STATE["traffic"] > 135 or SYSTEM_STATE["airQuality"] > 180 or SYSTEM_STATE["energyUsage"] > 110) and random.random() < 0.2:
            alert_id = f"ALT-{random.randint(1000, 9999)}"
            timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            desc = "CRITICAL METRICS EXCEEDED: Sector-wide infrastructure failure imminent. Crisis Mode Recommended."
            socketio.emit('new_alert', {
                "id": alert_id, "type": "Metric Threshold Breach", 
                "severity": "Extreme", "desc": desc
            })
            with get_db_connection() as conn:
                try:
                    conn.execute("INSERT INTO Alerts VALUES (?, ?, ?, ?, ?)", (alert_id, "Metric Threshold Breach", "Extreme", desc, timestamp))
                except Exception:
                    pass

        # Hard boundaries to prevent irrational mathematical numbers
        SYSTEM_STATE["traffic"] = max(10, min(150, SYSTEM_STATE["traffic"]))
        SYSTEM_STATE["airQuality"] = max(10, min(200, SYSTEM_STATE["airQuality"]))
        SYSTEM_STATE["energyUsage"] = max(10, min(120, SYSTEM_STATE["energyUsage"]))

        # Event-Driven Push: Broadcast new state universally to all connected clients
        socketio.emit('stats_update', get_current_stats())
