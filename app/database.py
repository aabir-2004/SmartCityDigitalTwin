import sqlite3
import os
from contextlib import contextmanager
from typing import Iterator

DB_PATH = os.environ.get('SMARTCITY_DB_PATH', 'smartcity.db')

@contextmanager
def get_db_connection() -> Iterator[sqlite3.Connection]:
    """Provide a transactional scope around a series of operations."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database() -> None:
    """Initialize the schema if it does not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Complaints (
                ComplaintID TEXT PRIMARY KEY,
                Category TEXT,
                Location TEXT,
                Description TEXT,
                Status TEXT,
                Timestamp TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Alerts (
                AlertID TEXT PRIMARY KEY,
                AlertType TEXT,
                Severity TEXT,
                Description TEXT,
                Timestamp TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AdminActions (
                ActionID TEXT PRIMARY KEY,
                ActionType TEXT,
                TargetLocation TEXT,
                Result TEXT,
                Timestamp TEXT
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM Complaints")
        if cursor.fetchone()[0] == 0:
            import random
            import time
            seed_complaints = [
                (f"CMP-{random.randint(1000, 9999)}", "Traffic", "Sector 3 Junction", "Severe traffic loop causing 45 min delays.", "Open", time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 1800))),
                (f"CMP-{random.randint(1000, 9999)}", "Infrastructure", "East Side Highway", "Street lights completely off on the main highway bridge.", "In Progress", time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 7200)))
            ]
            cursor.executemany("INSERT INTO Complaints VALUES (?, ?, ?, ?, ?, ?)", seed_complaints)
