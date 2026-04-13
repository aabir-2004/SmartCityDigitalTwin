import time
import random

SYSTEM_STATE = {
    "traffic": 60.0,
    "airQuality": 40.0,
    "energyUsage": 30.0,
    "traffic_trend": 0.5, 
    "airQuality_trend": 0.2,
    "energyUsage_trend": 0.1, 
}

def apply_admin_action(action_type):
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

def get_current_stats():
    return {
        "traffic": round(SYSTEM_STATE["traffic"], 1),
        "airQuality": round(SYSTEM_STATE["airQuality"], 1),
        "energyUsage": round(SYSTEM_STATE["energyUsage"], 1)
    }

def run_simulation_loop(socketio):
    """
    Background Task: Continuous time-evolving deterministic simulation.
    Drift + Trend + Noise mechanism influencing metrics every tick.
    """
    global SYSTEM_STATE
    while True:
        socketio.sleep(2.5) # Non-blocking sleep for WebSocket async loop
        
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

        # Hard boundaries to prevent irrational mathematical numbers
        SYSTEM_STATE["traffic"] = max(10, min(150, SYSTEM_STATE["traffic"]))
        SYSTEM_STATE["airQuality"] = max(10, min(200, SYSTEM_STATE["airQuality"]))
        SYSTEM_STATE["energyUsage"] = max(10, min(120, SYSTEM_STATE["energyUsage"]))

        # Event-Driven Push: Broadcast new state universally to all connected clients
        socketio.emit('stats_update', get_current_stats())
