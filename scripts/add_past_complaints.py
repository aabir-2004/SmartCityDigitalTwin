import sqlite3
import random
from datetime import datetime, timedelta

def add_past_complaints():
    conn = sqlite3.connect('smartcity.db')
    c = conn.cursor()
    
    # Check if we already have past complaints from 2023/2024
    c.execute("SELECT COUNT(*) FROM Complaints WHERE Timestamp LIKE '2023-%' OR Timestamp LIKE '2024-%'")
    count = c.fetchone()[0]
    
    if count < 3:
        needed = 3 - count
        complaints_data = []
        categories = ["Traffic", "Infrastructure", "Emergency", "Pollution", "General"]
        locations = ["Downtown Central Hub", "Sector 4 Industrial Park", "East Side Highway", "MG Road Intercept"]
        statuses = ["In Progress", "Resolved", "Open"]
        
        for _ in range(needed):
            cid = f"CMP-{random.randint(1000, 9999)}"
            category = random.choice(categories)
            loc = random.choice(locations)
            desc = f"Reported issue regarding {category.lower()} at {loc}. Requesting immediate attention."
            status = random.choice(statuses)
            
            # Generate random past date in 2023 or 2024
            year = random.choice([2023, 2024])
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            
            past_date = datetime(year, month, day, hour, minute)
            timestamp_str = past_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            complaints_data.append((cid, category, loc, desc, status, timestamp_str))
        
        c.executemany("INSERT INTO Complaints (ComplaintID, Category, Location, Description, Status, Timestamp) VALUES (?, ?, ?, ?, ?, ?)", complaints_data)
        conn.commit()
    conn.close()

if __name__ == "__main__":
    add_past_complaints()
