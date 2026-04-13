#!/bin/bash

echo "Starting Smart City Project..."

# Identify and kill any process already running on port 8080
PID=$(lsof -t -i:8080)
if [ ! -z "$PID" ]; then
    echo "Killing existing stale process on port 8080 (PID: $PID)..."
    kill -9 $PID
fi

# Activate the python virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment 'venv' not found in the current directory."
    exit 1
fi

# Optional: Seed the database if you want fresh data every run
# python scripts/seed_db.py

# Open the platform in your default web browser automatically (macOS command)
echo "Launching web browser automatically..."
(sleep 2 && open http://127.0.0.1:8080/) &

# Start the actual Flask Backend Server
echo "Starting backend server on port 8080..."
PORT=8080 python run.py
