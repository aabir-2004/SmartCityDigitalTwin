# Smart City Digital Twin 🏙️

Welcome to the **Smart City Digital Twin** project—a centralized, real-time smart city management ecosystem. This platform bridges the gap between civic administration and citizen engagement, utilizing historical datasets to simulate live IoT infrastructure metrics.

## 🚀 Key Features

* **Citizen Portal:** A sleek, user-friendly interface where citizens can report infrastructure complaints and submit emergent urban alerts.
* **Manager Governance Dashboard:** A real-time command center for administrators featuring interactive data visualizations (`Chart.js`), live polling of citizen feedback, and IoT sensor anomaly detection.
* **Realistic Data Engine:** Powered by authentic historical data feeds (Kaggle/OpenData) covering Air Quality (PM2.5), US Energy Loads, and Traffic hub logic. A live "micro-variance jitter" algorithm perfectly emulates real hardware sensor fluctuations.
* **Automated Setup:** Includes a seamless `run.sh` script that automatically handles environment setup, clears occupied ports, and launches the application.

## 🛠️ Technology Stack

* **Frontend:** Pure Vanilla HTML5, CSS3, ES6 JavaScript ("Soft UI" / Premium Flat Design).
* **Backend:** Python + Flask REST API.
* **Database:** SQLite3 (`smartcity.db`).
* **Data Processing:** Python `pandas` for data ingestion and synthesis.
* **Visualization Themes:** Chart.js + Lucide SVGs.

## 🚦 Getting Started

### Prerequisites
* **Python 3.x** installed.
* A UNIX-like terminal (macOS/Linux) to run the startup script.

### Installation & Execution

We have provided a streamlined bash script to start the project with a single command. 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aabir-2004/SmartCityDigitalTwin.git
   cd SmartCityDigitalTwin
   ```

2. **Run the Initialization Script:**
   ```bash
   ./run.sh
   ```
   
   **What this script does:**
   * Checks for and safely terminates any stale processes already running on Port `8080`.
   * Activates the local Python virtual environment (`venv`).
   * Starts the actual Flask backend server.
   * Automatically opens the platform dynamically in your default web browser at `http://127.0.0.1:8080`.

## 📂 Project Structure

* `/app/` - The core standalone Flask API, handling SQLite relational queries, and routing logic (`database.py`, `api/endpoints.py`).
* `/frontend/` - Contains all HTML routing interfaces (`index.html`, `citizen.html`, `admin.html`), CSS styling, and client-side JavaScript architecture.
* `/scripts/` - Database population engines (`seed_db.py`) cleaning and mapping historic data directly into SQL tables.
* `/DATASETS/` - Authentic `.csv` data representing Air Quality limits, regional Traffic, and macro-Energy consumption.

## 🔮 Future Roadmap
* **Full Duplex WebSockets:** Migrating from standard interval polling on the frontend to active `Socket.io` connections for true push-based latency reduction.
* **Predictive ML AI Modeling:** Integrating `scikit-learn` algorithms on historical sensor data to proactively predict traffic deadlocks and grid outages.
* **Hardware Integration:** Hooking up physical IoT micro-controllers (e.g., a Raspberry Pi) publishing metrics via an MQTT Broker to override the dataset simulation in real-time.

---
*Built for the future of urban analytics and systemic city infrastructure optimization.*
