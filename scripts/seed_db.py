import sqlite3
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get('SMARTCITY_DB_PATH', 'smartcity.db')

locations = [
    "Downtown Central Hub", "Sector 4 Industrial Park", "Northside Residential",
    "East Side Highway", "MG Road Intercept", "Airport Express Link", 
    "Green Valley Suburb", "City Hospital Junction", "Tech Park Avenue",
    "Riverfront Promenade", "Financial District", "Old Town Square"
]

issue_categories = ["Traffic", "Infrastructure", "Emergency", "Pollution", "General"]

complaint_desc_templates = {
    "Traffic": ["Massive gridlock due to {reason}.", "Traffic lights out, causing chaos.", "Accident blocking two lanes."],
    "Infrastructure": ["Pothole size of a crater.", "Water pipe burst, flooding street.", "Power lines down after storm.", "Streetlights not working for 3 days."],
    "Emergency": ["Suspected fire in commercial building.", "Medical emergency, need ambulance access.", "Severe flooding risk at the underpass."],
    "Pollution": ["Thick smog covering the area.", "Illegal garbage dumping in progress.", "Excessive noise from construction site late night."],
    "General": ["Stray animals causing nuisance.", "Graffiti on public monument.", "Request for new bus stop shelter."]
}

alert_types = [
    {"type": "Traffic Congestion Spike", "severity": "Warning", "desc": "Traffic velocity dropped below 15km/h in {loc}."},
    {"type": "Critical Air Quality", "severity": "Critical", "desc": "PM2.5 index exceeded 200 in {loc}."},
    {"type": "Power Grid Overload", "severity": "Warning", "desc": "Transformer load reached 95% capacity in {loc}."},
    {"type": "Flooding Detected", "severity": "Critical", "desc": "Water level sensors triggered in {loc} underpass."},
    {"type": "Infrastructure Failure", "severity": "Info", "desc": "Multiple streetlights reported offline in {loc}."}
]


def load_real_data_or_fallback(sensor_type, num_points=49):
    # Returns a list of num_points readings
    try:
        if sensor_type == "EnergyLoad":
            df = pd.read_csv("DATASETS/PJME_hourly.csv")
            # Grab a random contiguous slice of 49 hours
            start_idx = random.randint(0, len(df) - num_points - 1)
            # convert to MW to somewhat fit our 30-60MW scale, or just use raw divided by 1000
            vals = df["PJME_MW"].iloc[start_idx:start_idx+num_points].values / 1000.0 
            return list(vals)

        elif sensor_type == "AirQuality":
            df = pd.read_csv("DATASETS/ad_viz_plotval_data.csv")
            # It's daily. Let's just grab a bunch of AQI values and interpolate or just use them
            vals = list(df["Daily AQI Value"].dropna().values)
            random.shuffle(vals)
            # Since it's daily, let's create hourly noise around a base daily value
            hourly_vals = []
            for i in range(num_points):
                base = vals[i % len(vals)]
                hourly_vals.append(base + random.uniform(-2, 2))
            return hourly_vals

        elif sensor_type == "TrafficFlow":
            df = pd.read_csv("DATASETS/Traffic_Volume_Counts_(Historical)_20260305.csv")
            traffic_cols = ["12:00-1:00 AM", "1:00-2:00AM", "2:00-3:00AM", "3:00-4:00AM", "4:00-5:00AM", 
                            "5:00-6:00AM", "6:00-7:00AM", "7:00-8:00AM", "8:00-9:00AM", "9:00-10:00AM", 
                            "10:00-11:00AM", "11:00-12:00PM", "12:00-1:00PM", "1:00-2:00PM", "2:00-3:00PM", 
                            "3:00-4:00PM", "4:00-5:00PM", "5:00-6:00PM", "6:00-7:00PM", "7:00-8:00PM", 
                            "8:00-9:00PM", "9:00-10:00PM", "10:00-11:00PM", "11:00-12:00AM"]
            
            # Pick a few random rows to cover 49 hours
            rows_needed = (num_points // 24) + 1
            sample_df = df.sample(n=rows_needed)
            
            raw_vals = []
            for _, row in sample_df.iterrows():
                for col in traffic_cols:
                    val = str(row[col]).replace(',','')
                    try:
                        raw_vals.append(float(val))
                    except:
                        raw_vals.append(50.0) # default fallback for unparseable
            return raw_vals[:num_points]

    except Exception as e:
        logger.warning(f"Could not load real data for {sensor_type}. Falling back to synthetic generators. Error: {e}")
        # Synthetic fallback
        vals = []
        for hours_ago in range(num_points-1, -1, -1):
            is_rush_hour = (24 - hours_ago % 24) in (8, 9, 17, 18)
            if sensor_type == "TrafficFlow":
                base = random.randint(150, 250) if is_rush_hour else random.randint(30, 80)
            elif sensor_type == "AirQuality":
                base = random.randint(100, 160) if is_rush_hour else random.randint(40, 90)
            else: # EnergyLoad
                base = random.uniform(50, 60) if (18 <= (24 - hours_ago % 24) <= 22) else random.uniform(30, 40)
            vals.append(base + random.uniform(-10, 10))
        return vals

def create_realistic_db():
    logger.info("Initializing hybrid (historical + synthesized) database schema...")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS Complaints 
                     (ComplaintID TEXT PRIMARY KEY, Category TEXT, Location TEXT, Description TEXT, Status TEXT, Timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS Alerts 
                     (AlertID TEXT PRIMARY KEY, AlertType TEXT, Severity TEXT, Description TEXT, Timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS SensorData
                     (SensorID TEXT, Location TEXT, SensorType TEXT, Reading REAL, Status TEXT, Timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS AdminActions
                     (ActionID TEXT PRIMARY KEY, ActionType TEXT, TargetLocation TEXT, Result TEXT, Timestamp TEXT)''')
        
        c.execute("DELETE FROM Complaints")
        c.execute("DELETE FROM Alerts")
        c.execute("DELETE FROM SensorData")
        c.execute("DELETE FROM AdminActions")
        
        conn.commit()
        
        # 1. Complaints (Synthetic since no dataset provided)
        logger.info("Generating realistic citizen complaints...")
        complaints_data = []
        now = datetime.now()
        
        for i in range(100):
            cid = f"CMP-{random.randint(10000, 99999)}-{i}"
            category = random.choices(issue_categories, weights=[0.4, 0.3, 0.1, 0.1, 0.1])[0]
            loc = random.choice(locations)
            
            reasons = ["construction", "accident", "VIP movement", "heavy rain"]
            desc_template = random.choice(complaint_desc_templates[category])
            desc = desc_template.format(reason=random.choice(reasons))
            
            status = random.choices(["Open", "In Progress", "Resolved", "Closed"], weights=[0.2, 0.3, 0.4, 0.1])[0]
            
            past_time = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            timestamp_str = past_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            complaints_data.append((cid, category, loc, desc, status, timestamp_str))
            
        c.executemany("INSERT INTO Complaints VALUES (?, ?, ?, ?, ?, ?)", complaints_data)
        
        # 2. Alerts (Synthetic)
        logger.info("Generating system alerts...")
        alerts_data = []
        for i in range(50):
            aid = f"ALT-{random.randint(10000, 99999)}-{i}"
            alert_template = random.choice(alert_types)
            loc = random.choice(locations)
            desc = alert_template['desc'].format(loc=loc)
            
            past_time = now - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            timestamp_str = past_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            alerts_data.append((aid, alert_template['type'], alert_template['severity'], desc, timestamp_str))
            
        c.executemany("INSERT INTO Alerts VALUES (?, ?, ?, ?, ?)", alerts_data)
        
        # 3. Sensor Data (Hybrid - pull from datasets where available)
        logger.info("Processing historic IoT telemetry streams...")
        sensor_data = []
        
        for loc in locations[:5]: # Top 5 locs
            traffic_readings = load_real_data_or_fallback("TrafficFlow", 49)
            aqi_readings = load_real_data_or_fallback("AirQuality", 49)
            energy_readings = load_real_data_or_fallback("EnergyLoad", 49)

            # Insert backwards from -48 hours to 0
            for i in range(49):
                hours_ago = 48 - i
                read_time = now - timedelta(hours=hours_ago)
                time_str = read_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                sensor_data.append((f"SENS-TRF-{loc[:3].upper()}", loc, "TrafficFlow", round(traffic_readings[i], 2), "Active", time_str))
                sensor_data.append((f"SENS-AQI-{loc[:3].upper()}", loc, "AirQuality", round(aqi_readings[i], 2), "Active", time_str))
                sensor_data.append((f"SENS-ENG-{loc[:3].upper()}", loc, "EnergyLoad", round(energy_readings[i], 2), "Active", time_str))

        c.executemany("INSERT INTO SensorData VALUES (?, ?, ?, ?, ?, ?)", sensor_data)
        conn.commit()
        logger.info("Database provisioning complete.")

if __name__ == '__main__':
    create_realistic_db()
