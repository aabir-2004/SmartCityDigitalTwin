# Smart City Digital Twin

Smart City Digital Twin is a comprehensive system for real-time urban infrastructure monitoring and citizen feedback management. It integrates citizen-reported data with historical sensor metrics to provide a centralized governance dashboard for city administrators.

The system is designed to simulate authentic IoT environments by utilizing real-world datasets rather than arbitrary mathematically generated logic. It enforces a strict boundary between public reporting and administrative action, ensuring clean, verifiable data layers across the platform.

---

## System Overview

At a high level, the pipeline ingests public infrastructural complaints and historical environment data, processes them through a unified backend, and dynamically renders actionable insights on a real-time command dashboard.

Citizen Feedback & OpenData → Flask REST Backend  
→ Relational Persistence (SQLite) → Asynchronous Polling  
→ Data Visualization (Chart.js) → Manager Action  

The public datasets serve as simulated sensor readings. All subsequent routing handles these data points identically to live IoT hardware polling.

---

## Design Principles

The system is built around a few core constraints:

- All visual dashboard metrics are grounded strictly in the database state, eliminating arbitrary frontend mock data.  
- Simulated hardware variance is algorithmically applied to historical data to reproduce authentic sensor fluctuations.  
- Interactions are entirely decoupled; the Citizen module and the Manager panel operate in strict isolation via REST endpoints.  
- The frontend architecture eschews heavy frameworks in favor of high-performance Vanilla JS and "Soft UI" aesthetics.  


This ensures that the environment operates efficiently, reliably, and can easily transition to physical hardware integration (e.g., Raspberry Pi/MQTT) without core logic rewrites.

---

## Architecture

The backend is implemented using a monolithic Python Flask API that handles all data processing, logical state changes, and simulated hardware data synthesis. 

<img width="1141" height="710" alt="Screenshot 2026-04-14 at 12 20 51 AM" src="https://github.com/user-attachments/assets/19fb6f39-e028-43a5-877a-f5045652fcb5" />

The frontend is built with pure HTML5, CSS3, and ES6 JavaScript, providing controlled interfaces for dataset visualization and civil reporting. 

A local embedded SQLite layer is used for instantaneous data persistence and retrieval, reducing overhead and maximizing local deployment reliability.

---

## Pipeline Description

### Data Ingestion

Historic, real-world datasets encompassing US Energy Loads, Air Quality (PM2.5), and Traffic arrays are ingested via server-side pipelines (`seed_db.py`). The data is cleaned and optimally formatted for fast querying.

### Citizen Reporting Logic

The Citizen portal provides isolated structural submission boundaries. Feedback is structured as `JSON` and POSTed securely to the backend. No structural or schema-based changes are permitted from the client interface layer.

### Visualization & Variance Engine

The Manager dashboard pulls metric distributions via asynchronous fetches. A custom "micro-variance jitter" algorithm applies algorithmic noise over standard historical data, perfectly emulating the live drift of hardware sensors inside the `Chart.js` rendering cycle.

### Management & Control

A dedicated polling loop updates the Administrator dashboard dynamically. Administrative override actions (such as acknowledging or resolving a city alert) alter state records mathematically, allowing the system to reflect changes in real-time.

---

## Infrastructure and Reliability

Process integrity is enforced automatically across all layers:

- Dedicated virtual environments maintain dependency chains.  
- The backend application binds strictly to port `8080`, deliberately evading default macOS AirPlay conflicts.  
- Invalid or malformed POST requests from the Citizen interface are filtered before execution.  

This ensures identical deployment states across multiple operating systems.

---

## Deployment

The system leverages a localized deployment orchestrator (`run.sh`) to automate the environment.

Execution flow automatically processes:
- Port scanning and old daemon termination
- Virtual environment activation
- Server application logic bootstrap
- Dynamic web browser attachment

Run the system instantaneously via:
```bash
./run.sh
```

---

## License

All rights reserved.

Unauthorized copying, modification, distribution, or use of this software, in whole or in part, is strictly prohibited without prior written permission from the author.
