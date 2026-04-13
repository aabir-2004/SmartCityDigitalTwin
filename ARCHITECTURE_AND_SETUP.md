# Smart City Digital Twin — Codebase Architecture & Reference Guide

This document provides a highly detailed, file-by-file breakdown of the Smart City Digital Twin project. It is intended to serve as a comprehensive context mapping for future debugging, LLM context windows, and feature engineering, preventing the need to blindly traverse the repository.

---

## 1. High-Level Architecture Overview

The system is a deterministic, **Monolithic Client-Server Architecture** utilizing a **RESTful Python API** tightly coupled with an embedded **SQLite3** database. 

- **Frontend:** Pure HTML5/CSS3 and Vanilla ES6 JavaScript ("Soft UI" / Flat Design). It is explicitly broken apart into Citizen logic and Administrator logic.
- **Backend Core:** `Flask` forms the routing backbone, mapping JSON endpoints. 
- **Persistency Layer:** `SQLite3` via standard `sqlite3` driver. 
- **Analytics Mocking Mechanism:** Heavy dataset reliance (parsing Kaggle/OpenData arrays) overlaid with live mathematical "jitter" models to perfectly replicate hardware sensor output without physical hardware dependency.

---

## 2. Directory & Component Breakdown

### 2.1 The Root Execution Layer

**`run.sh`**
- **Role:** The primary system orchestrator for local deployment.
- **Functions / Steps Executed:** 
  1. Inspects Port `8080` (resolves macOS AirPlay collision specifically) via `lsof` and uses `kill -9` to purge stale daemons.
  2. Activates the Python virtual environment (`source venv/bin/activate`).
  3. Spawns an asynchronous timer `(sleep 2 && open http://127.0.0.1:8080)` to dynamically inject the app into the default browser.
  4. Triggers the actual application binary `PORT=8080 python run.py`.

**`run.py`**
- **Role:** The Python entry point bootstrapping the Flask server framework.
- **Mechanism:** Imports the `create_app` factory from the `app/` package structure. It explicitly runs the `flask_app` locally on `127.0.0.1:8080` with debugging enabled but the auto-reloader turned off (`use_reloader=False`) to avoid multiple parallel boots inside the bash wrapper.

---

### 2.2 The Backend Application (`/app`)

**`app/__init__.py`**
- **Role:** The Flask Application Factory.
- **Key Actions:** 
  - Initiates the `Flask(__name__)` app context.
  - Directs static file loading specifically to the `frontend` directory.
  - Re-routes the index (`/`) endpoint to load `index.html`.
  - Registers the API Blueprint (`api_bp`) to prefix all backend calls with `/api`.
  - Calls `initialize_database()` (from `app.database`) on boot to ensure schema integrity immediately.

**`app/database.py`**
- **Role:** Primary Database Interface resolving relational queries.
- **Functions:**
  - `get_db_connection() -> Iterator[sqlite3.Connection]`
    Utilizes the `@contextmanager` decorator wrapping standard SQLite connections within a `try/except/finally` transaction block. Ensures atomic commits and auto-rollback on failure. Sets `row_factory = sqlite3.Row` for dictionary-like data returning.
  - `initialize_database() -> None`
    Checks local DB context. If no schema is found, runs `CREATE TABLE IF NOT EXISTS` for `Complaints`, `Alerts`, and `AdminActions`. Validates the row count of `Complaints`; if perfectly empty, it triggers an initial data seed inserting two mock historic complaints to populate early interactions.

**`app/api/endpoints.py`**
- **Role:** The strict routing logic processing POST payloads and distributing GET analytical reads.
- **Functions:**
  - `@api_bp.route('/complaints', methods=['POST']) -> add_complaint()`: Captures JSON payloads from `citizen.js`. Asserts keys (`category`, `location`, `description`). Generates a custom UUID (`CMP-xxxx`), injects into storage, and returns `201 Created`.
  - `@api_bp.route('/complaints', methods=['GET']) -> get_complaints()`: Standard data pull fetching all records from `Complaints` ordering entirely by descending `Timestamp` structure.
  - `@api_bp.route('/dashboard/stats', methods=['GET']) -> get_dashboard_stats()`: The primary data-mocking mathematical engine for the Chart.js widgets. It pulls the single latest `SensorData` recording, and applies a `random.uniform()` algorithmic variance ("jitter" of ±2%) to perfectly emulate the visual appearance of actively streaming physical sensor updates.
  - `@api_bp.route('/dashboard/alerts', methods=['GET']) -> get_system_alerts()`: Retrieves the 5 latest system anomalies. Features deterministic behavior: ~25% of all calls secretly trigger `_trigger_synthetic_anomaly()` in the background to inject realistic active problems automatically.
  - `_trigger_synthetic_anomaly() -> None`: An internal helper function that selects a live city location block and randomly drops a synthesized "Warning" or "Critical" alert (e.g. Traffic Congestion, Grid Optimization) into the SQL schema.
  - `@api_bp.route('/actions/trigger', methods=['POST']) -> trigger_action()`: An interactive pipeline allowing administrators to bypass system events and write automated resolutions directly into the `AdminActions` historical table.

---

### 2.3 Analytics Pipeline (`/scripts`)

**`scripts/seed_db.py`**
- **Role:** Extract, Transform, Load (ETL) pipeline for large-scale simulated data.
- **Mechanism:** Leverages `pandas` to open actual external CSVs (`DATASETS/`). It scrubs the rows of anomalous NULL readings and maps them systematically into the lightweight `smartcity.db` `SensorData` architecture. Requires manual execution if the system is to be structurally initialized with raw machine learning sets.

---

### 2.4 User Interface Layer (`/frontend`)

**`frontend/index.html`**
- Provides the role-assignment portal ("Citizen" vs "Manager").

**`frontend/citizen.html` & `/js/citizen.js`**
- **Role:** Publicly accessible payload constructor.
- Provides forms intercepting HTML `submit` behavior, capturing `<input>` values, and firing an `await fetch('/api/complaints', { method: 'POST' })` payload. Replaces the local DOM logic dynamically upon submission indicating resolution without page reload.

**`frontend/admin.html` & `/js/admin.js`**
- **Role:** Core Administrative Graphical Monitoring Panel.
- **Functions Managed:**
  - Instantiates complex visual artifacts utilizing `Chart.js`.
  - Runs continuous asynchronous `setInterval()` polling loops mapping to `/api/dashboard/stats` updating DOM text layers with newly retrieved jitter-metrics.
  - Re-triggers table reconstruction asynchronously by `fetch()` pulling on `/api/complaints`.

---

## 3. How To Use Context

When generating or debugging code within this system:

1. **Schema Consistency:** If adding sensors, you must verify the table definition in `database.py:initialize_database()` and align the REST query in `endpoints.py`.
2. **Deterministic Responses:** Avoid writing backend routes that return non-seeded stochastic logic without appending the action statically into the `sqlite3` historical ledger first.
3. **Data Integrity Checks:** Never append raw form inputs. Use `request.get_json()` strictly, check valid schema keys manually before triggering atomic transactions in `database.py`.

## 4. Execution Command Flow

If testing local execution independently:
```bash
./run.sh
```
*(Automates port clearance, virtual environment linking, backend REST startup, and browser orchestration.)*
