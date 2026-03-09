# Smart City Digital Twin - Development Log & Architecture Document

## 1. Project Overview
This document outlines the architecture, progress, methodology, and module structure of the **Smart City Digital Twin** project. Built to spec from `SRS.json` and the project PDF requirements, this system acts as a centralized smart city management ecosystem. 

It consists of two main branches:
1. **Citizen Module:** Where citizens report infrastructure complaints and emergent alerts.
2. **Manager Panel (Admin Dashboard):** A real-time command center focusing on core IoT metrics, anomaly alerts, and structured citizen feedback.

---

## 2. Methodology & Progress Made

The project is built on a **Client-Server Architecture** utilizing a Vanilla HTML/CSS/JS frontend and a Python Flask REST API backend. 

### Phase 1: Frontend Construction & Aesthetics
- **Initial Build:** We successfully built the UI starting with pure HTML/CSS and JavaScript, avoiding heavy framework overhead. Data was initially simulated via frontend `localStorage` to validate design.
- **"Soft UI" Overhaul:** Based on specific template feedback, we transformed the UI into a sleek, premium, flat-design light theme dashboard layout.
- **Aesthetic Refinement:** Purged all emojis (replaced systematically with `Lucide` SVGs), eliminated complex gradients, and implemented a crisp data-science color palette (True Blue `#2563EB`, Navy `#1E3A5F`, Desaturated Blue `#4A6FA5`) ensuring ultimate professionalism.

### Phase 2: Backend Architecture & Integration
- Created a monolithic Python Flask backend API (`app.py`) to manage relational data, completely sunsetting the original `data-sim.js` mocked logic.
- Implemented real `async/await` fetch behavior in the frontend, securely routing data points to and from the server.
- Resolved tricky macOS deployment conflicts (AirPlay Receiver port collisions on ports 5000 and 8000), permanently and cleanly binding the server to `Port 8080`.

### Phase 3: Realistic Data Engineering (Data Science Upgrade)
- Transitioned the app from using naive random mathematical numbers to serving **authentic historical data feeds**.
- Researched, procured, and integrated Kaggle/OpenData CSVs containing real-world datasets spanning **Traffic Hub logic, US Energy Loads, and Air Quality (PM2.5)** into the environment.
- Developed the data ingestion pipeline (`seed_db.py`) utilizing `pandas` to organically synthesize 100 structured complaints, 50 alerts, and massive amounts of `SensorData` history. 
- Integrated a live algorithmic "micro-variance jitter" on the historical dataset to perfectly emulate live IoT hardware fluctuations onto the Chart.js widgets.

---

## 3. Codebase Structure (What Code Serves What Purpose)

### 3.1 Frontend (`frontend/`)
- `index.html`: The landing portal hub to select personas (Citizen/Manager).
- `citizen.html` & `js/citizen.js`: The frontend interface that enables Citizens to seamlessly submit infrastructural feedback via POST to the server.
- `admin.html` & `js/admin.js`: The comprehensive Manager Governance Dashboard rendering `Chart.js` components, live polling table data for tracking Citizen issues (`GET /api/complaints`), and system Action overrides.
- `css/styles.css`: The central flat-design stylesheet housing the synchronized theme variables, drop-shadow configurations, and "Soft UI" aesthetics.

### 3.2 Backend Engine
- `app.py`: The core standalone Flask API framework processing RESTful routes, mapping JSON, rendering endpoints (`/api/dashboard/stats`, `/api/complaints`), and interacting with the database.
- `seed_db.py`: Database population script. Automatically cleans, maps, and distributes historic data taken from the `DATASETS/` folder directly into SQL to seed the engine when necessary.
- `smartcity.db`: The local `sqlite3` database maintaining strictly relational tables: `Complaints`, `Alerts`, `SensorData`, and `AdminActions`.
- `app.log`: Server log retaining traceback and asynchronous interaction histories.

### 3.3 Core Configuration
- `DATASETS/`: Directory staging actual `.csv` files representing historical Air Quality limits, regional Traffic, and macro-Energy consumption.
- `real_world_data_guide.json`: A static map identifying ideal dataset columns, structures, and sources for adding future complex datasets.
- `SRS.json`: The Software Requirements Specification driving the feature set logic.

---

## 4. Pending Tasks & Future Work

While the primary environment operates cohesively, the following features remain scoped as Future Work:
- **WebSockets Migration:** Migrate the `admin.js` dashboard from interval loop polling (requesting the backend every `x` seconds) to full duplex `WebSocket / Socket.io` active connections for true push-based latency reduction.
- **Predictive ML Modeling:** Implement `scikit-learn` algorithms in `app.py` taking historical `SensorData` to proactively predict likely grid-outages or traffic deadlocks rather than just displaying historical averages.
- **Authentication Gate:** Implement a JWT or session-based authentication loop for the Administrator view.
- **Hardware Integration:** Connect a true IoT micro-controller (e.g., Raspberry Pi) publishing through an MQTT Broker to override the dataset simulation in real-time.
