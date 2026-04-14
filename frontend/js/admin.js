class AdminDashboard {
    constructor() {
        this.pollRates = {
            stats: 2000,
            complaints: 5000,
            alerts: 4000
        };
        this.chartInstances = {};
        this.alertRegistry = new Set();
        this.complaintRegistry = new Set();
        this.markers = {};

        this.domReferences();
        this.initializeMap();
        this.initializeCharts();
        this.attachGlobalActions();

        // WebSocket Integration for true real-time updates
        this.setupWebSockets();
        this.fetchLocations();
    }

    domReferences() {
        this.nodes = {
            trafficVal: document.getElementById('trafficVal'),
            aqiVal: document.getElementById('aqiVal'),
            energyVal: document.getElementById('energyVal'),
            alertsContainer: document.getElementById('alertsContainer'),
            complaintBody: document.getElementById('complaintTableBody'),
            actionStatusContainer: document.getElementById('actionStatus'),
            actionStatusText: document.getElementById('actionStatusText'),
            cityMap: document.getElementById('cityMap')
        };
    }

    getChartConfiguration() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            elements: {
                line: { tension: 0.35 },
                point: { radius: 0 }
            }
        };
    }

    buildTimeseries(contextId, strokeColor, fillColor) {
        const canvas = document.getElementById(contextId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: new Array(20).fill(''),
                datasets: [{
                    data: new Array(20).fill(0).map(() => Math.floor(Math.random() * 40) + 20),
                    borderColor: strokeColor,
                    backgroundColor: fillColor,
                    borderWidth: 3,
                    fill: true
                }]
            },
            options: this.getChartConfiguration()
        });
    }

    initializeCharts() {
        this.chartInstances = {
            traffic: this.buildTimeseries('trafficChart', '#1d7af0', 'rgba(29, 122, 240, 0.2)'),
            aqi: this.buildTimeseries('aqiChart', '#05CD99', 'rgba(5, 205, 153, 0.2)'),
            energy: this.buildTimeseries('energyChart', '#b388ff', 'rgba(179, 136, 255, 0.2)')
        };
    }

    initializeMap() {
        if (!this.nodes.cityMap || typeof L === 'undefined') return;

        // Base New York coordinate
        this.map = L.map('cityMap').setView([40.7128, -74.0060], 12);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }).addTo(this.map);
    }

    getLocationCoordinates(locationName) {
        // Handpicked terrestrial GPS coordinates across New York City zones
        const nycZoningMap = {
            "Downtown Central Hub": [40.7580, -73.9855], // Midtown/Times Sq
            "Sector 4 Industrial Park": [40.7022, -73.9739], // Brooklyn Navy Yard
            "Northside Residential": [40.7870, -73.9754], // Upper West Side
            "East Side Highway": [40.7225, -73.9734], // FDR/East Village
            "MG Road Intercept": [40.7188, -74.0016], // Tribeca/Canal St
            "Airport Express Link": [40.7716, -73.8744], // LaGuardia proximity
            "Green Valley Suburb": [40.6602, -73.9690], // Prospect Park
            "City Hospital Junction": [40.7903, -73.9525], // Mount Sinai area
            "Tech Park Avenue": [40.7411, -73.9897], // Silicon Alley/Flatiron
            "Riverfront Promenade": [40.7116, -74.0163], // Battery Park City
            "Financial District": [40.7075, -74.0113], // Wall St
            "Old Town Square": [40.7308, -73.9973] // Washington Sq Park
        };

        if (nycZoningMap[locationName]) {
            return nycZoningMap[locationName];
        }

        // Deterministic fallback array of guaranteed dry-land points in NYC in case of new sectors
        const safeLandPoints = [
            [40.7282, -73.9942], [40.7356, -74.0012], [40.6925, -73.9904],
            [40.8093, -73.9485], [40.7614, -73.9776], [40.8296, -73.9262]
        ];

        let hash = 0;
        for (let i = 0; i < locationName.length; i++) {
            hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
        }

        return safeLandPoints[Math.abs(hash) % safeLandPoints.length];
    }

    processTelemetry(metrics) {
        try {

            if (this.nodes.trafficVal) this.nodes.trafficVal.textContent = metrics.traffic;
            if (this.nodes.aqiVal) this.nodes.aqiVal.textContent = metrics.airQuality || metrics.aqi;
            if (this.nodes.energyVal) this.nodes.energyVal.textContent = metrics.energyUsage;

            const mappings = [
                { id: 'traffic', value: metrics.traffic },
                { id: 'aqi', value: metrics.airQuality },
                { id: 'energy', value: parseFloat(metrics.energyUsage) }
            ];

            mappings.forEach(mapping => {
                const chart = this.chartInstances[mapping.id];
                if (!chart) return;

                const seriesData = chart.data.datasets[0].data;
                seriesData.push(mapping.value);
                seriesData.shift();
                chart.update('none');
            });

        } catch (err) {
            console.warn('[Telemetry] Sync degraded:', err);
        }
    }

    async fetchAdminComplaints() {
        try {
            const req = await fetch('/api/complaints');
            if (!req.ok) return;

            const logs = await req.json();

            // Rebuild table DOM if present
            if (this.nodes.complaintBody) {
                this.nodes.complaintBody.innerHTML = '';
            }

            logs.forEach(record => {
                // Map visualization logic
                if (!this.complaintRegistry.has(record.ComplaintID || record.id)) {
                    this.complaintRegistry.add(record.ComplaintID || record.id);
                    
                    if (this.map) {
                        let loc = record.location || record.Location;
                        if (this.markers[loc]) {
                            const marker = this.markers[loc];
                            const popupContent = `<b>${loc}</b><br><span style="color:#8b5cf6;">Recent Complaint: ${record.category || record.Category}</span>`;
                            marker.setPopupContent(popupContent);

                            // Create a subtle ping
                            const alertColorHex = '#8b5cf6'; // purple
                            const circle = L.circle(marker.getLatLng(), {
                                color: alertColorHex,
                                fillColor: alertColorHex,
                                fillOpacity: 0.4,
                                radius: 800
                            }).addTo(this.map);

                            setTimeout(() => {
                                if (this.map) this.map.removeLayer(circle);
                            }, 5000);
                        }
                    }
                }

                // Table rendering logic
                if (this.nodes.complaintBody) {
                    const row = document.createElement('tr');
                    const badgeState = record.status === 'Open' ? 'badge-open' : 'badge-progress';

                    row.innerHTML = `
                        <td><strong>${record.id || record.ComplaintID}</strong></td>
                        <td>${record.category || record.Category}</td>
                        <td>${record.location || record.Location}</td>
                        <td>${record.description || record.Description}</td>
                        <td><span class="badge ${badgeState}">${record.status || record.Status}</span></td>
                        <td>${new Date(record.timestamp || record.Timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                    `;
                    this.nodes.complaintBody.appendChild(row);
                }
            });

        } catch (err) {
            console.warn('[Complaints] Fetch cycle skipped:', err);
        }
    }

    async pollSystemAlerts() {
        if (!this.nodes.alertsContainer) return;

        try {
            const req = await fetch('/api/dashboard/alerts');
            if (!req.ok) return;

            const items = await req.json();

            items.reverse().forEach(evt => {
                this.handleIncomingAlert(evt);
            });
        } catch (err) {
            console.warn('[Alerts] Engine disconnected:', err);
        }
    }

    handleIncomingAlert(evt) {
        if (!this.nodes.alertsContainer) return;
        
        if (!this.alertRegistry.has(evt.id || evt.AlertID)) {
            const id = evt.id || evt.AlertID;
            this.alertRegistry.add(id);

            let notificationClass = 'alert-info';
            let alertColorHex = '#3b82f6';

            if (evt.severity === 'Extreme') {
                notificationClass = 'alert-critical';
                alertColorHex = '#b91c1c';
                
                // Show pinned banner for Extreme Alerts
                if (!document.getElementById('extremeAlertBanner')) {
                    const banner = document.createElement('div');
                    banner.id = 'extremeAlertBanner';
                    banner.className = 'extreme-alert-banner';
                    banner.innerHTML = `
                        <div>
                            <span style="font-size: 1.25rem; margin-right: 15px;">⚠️ EXTREME ALERT</span>
                            ${evt.desc}
                        </div>
                        <button class="btn btn-secondary" onclick="window.dashboardController.toggleCrisisMode(true)" style="background: rgba(255,255,255,0.2); border: 1px solid white;">
                            ENABLE CRISIS MODE
                        </button>
                    `;
                    document.body.prepend(banner);
                }
            } else if (evt.severity === 'Critical') {
                notificationClass = 'alert-critical';
                alertColorHex = '#ef4444';
            } else if (evt.severity === 'Warning') {
                notificationClass = 'alert-warning';
                alertColorHex = '#f59e0b';
            }

            // Map specific logic: Search description for a known location
            let matchedLoc = null;
            for (let loc of Object.keys(this.markers)) {
                if (evt.desc.includes(loc)) {
                    matchedLoc = loc;
                    break;
                }
            }

            if (this.map && matchedLoc && this.markers[matchedLoc]) {
                const marker = this.markers[matchedLoc];
                marker.setPopupContent(`<b>${matchedLoc}</b><br><span style="color:${alertColorHex}">${evt.severity}: ${evt.type}</span>`);

                // Create a ping visual effect
                const circle = L.circle(marker.getLatLng(), {
                    color: alertColorHex,
                    fillColor: alertColorHex,
                    fillOpacity: 0.4,
                    radius: 1200
                }).addTo(this.map);

                this.map.panTo(marker.getLatLng());

                // Remove ping circle after 5s
                setTimeout(() => {
                    if (this.map) this.map.removeLayer(circle);
                }, 5000);
            }

            const alertBlock = document.createElement('div');
            alertBlock.className = `alert-item ${notificationClass} fade-in`;
            // Ensure timestamp exists, or fallback to current time
            const timeObj = evt.timestamp ? new Date(evt.timestamp) : new Date();
            
            alertBlock.innerHTML = `
                <div class="alert-header">
                    <span class="alert-title">${evt.severity} - ${evt.type}</span>
                    <span class="alert-time">${timeObj.toLocaleTimeString()}</span>
                </div>
                <div class="alert-desc">${evt.desc}</div>
            `;

            this.nodes.alertsContainer.prepend(alertBlock);

            if (this.nodes.alertsContainer.children.length > 5) {
                this.nodes.alertsContainer.lastElementChild.remove();
            }
        }
    }

    async fetchLocations() {
        try {
            const req = await fetch('/api/locations');
            if (req.ok) {
                const locations = await req.json();
                const selects = document.querySelectorAll('.location-select');
                selects.forEach(select => {
                    select.innerHTML = '<option value="" disabled selected>Select Target Sector...</option>';
                    locations.forEach(loc => {
                        const opt = document.createElement('option');
                        opt.value = loc;
                        opt.textContent = loc;
                        select.appendChild(opt);
                    });
                });

                if (this.map) {
                    // Populate GPS map markers
                    locations.forEach(loc => {
                        const coords = this.getLocationCoordinates(loc);
                        const marker = L.marker(coords).addTo(this.map)
                            .bindPopup(`<b>${loc}</b><br><span style="color:var(--status-success);">Status: Operating Normally</span>`);
                        this.markers[loc] = marker;
                    });
                }
            }
        } catch (err) {
            console.warn('[Locations] Could not fetch locations:', err);
        }
    }

    dispatchProcedure(actionType) {
        if (!this.nodes.actionStatusContainer) return;

        let location = 'City-Wide';
        const select = document.getElementById('actionLocationSelect');
        if (select && select.value) {
            location = select.value;
        }

        this.nodes.actionStatusContainer.style.display = 'block';
        this.nodes.actionStatusContainer.className = 'alert-item alert-critical fade-in';
        this.nodes.actionStatusText.innerHTML = `<strong>Command Sent:</strong> Deploying directive to ${location}...`;

        fetch('/api/actions/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ actionType: actionType, location: location })
        })
            .then(res => res.json())
            .then(data => {
                this.nodes.actionStatusContainer.className = 'alert-item alert-info fade-in';
                this.nodes.actionStatusText.innerHTML = `<strong>Execution Complete:</strong> ${data.message || actionType}`;
            })
            .catch(() => {
                this.nodes.actionStatusContainer.className = 'alert-item alert-danger fade-in';
                this.nodes.actionStatusText.innerHTML = `<strong>Error:</strong> Procedure execution halted by upstream.`;
            })
            .finally(() => {
                setTimeout(() => {
                    this.nodes.actionStatusContainer.style.display = 'none';
                }, 4500);
            });
    }

    toggleCrisisMode(active = null) {
        let isPresent = document.body.classList.contains('crisis-mode');
        let newActive = active !== null ? active : !isPresent;
        fetch('/api/crisis_mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({active: newActive})
        });
        
        // Remove banner if deactivating via global logic
        let banner = document.getElementById('extremeAlertBanner');
        if (!newActive && banner) banner.remove();
        
        let crisisCtls = document.getElementById('crisisAdditionalControls');
        if (crisisCtls) crisisCtls.style.display = newActive ? 'flex' : 'none';
    }

    async loadHeatmap(filterType = "all") {
        if (!this.map || typeof L.heatLayer === 'undefined') return;

        try {
            const req = await fetch('/api/resources');
            if (!req.ok) return;
            const resources = await req.json();

            // Format for Leaflet heat [lat, lng, intensity]
            let heatPoints = resources
                .filter(r => filterType === "all" || r.type === filterType)
                .map(r => [r.lat, r.lng, r.intensity]);

            if (this.heatLayer) {
                this.map.removeLayer(this.heatLayer);
            }

            this.heatLayer = L.heatLayer(heatPoints, {
                radius: 25,
                blur: 15,
                maxZoom: 14,
                gradient: {
                    0.2: 'blue',
                    0.4: 'cyan',
                    0.6: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'
                }
            }).addTo(this.map);
            this.heatmapActive = true;
        } catch (err) {
            console.warn('[Heatmap] Error loading resources:', err);
        }
    }

    toggleHeatmap() {
        if (!this.map) return;
        if (!this.heatLayer) {
            this.loadHeatmap(document.getElementById('heatmapFilter')?.value || 'all');
            return;
        }
        
        if (this.heatmapActive) {
            this.map.removeLayer(this.heatLayer);
            this.heatmapActive = false;
        } else {
            this.heatLayer.addTo(this.map);
            this.heatmapActive = true;
        }
    }

    attachGlobalActions() {
        // Expose dispatch to global scope for inline HTML event handlers
        window.simulateAction = this.dispatchProcedure.bind(this);

        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();

                // Filter complaints
                if (this.nodes.complaintBody) {
                    const rows = this.nodes.complaintBody.querySelectorAll('tr');
                    rows.forEach(row => {
                        row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
                    });
                }

                // Filter alerts
                if (this.nodes.alertsContainer) {
                    const alerts = this.nodes.alertsContainer.querySelectorAll('.alert-item');
                    alerts.forEach(alert => {
                        // ignore the emergency action alert items
                        if (alert.id === 'actionStatus') return;
                        alert.style.display = alert.textContent.toLowerCase().includes(term) ? '' : 'none';
                    });
                }
            });
        }
    }

    setupWebSockets() {
        // Initialize WebSocket connection to identical origin
        const socket = io();

        // Bind incoming websocket events
        socket.on('stats_update', (metrics) => {
            this.processTelemetry(metrics);
        });

        socket.on('new_complaint', () => {
            this.fetchAdminComplaints();
        });

        socket.on('new_alert', (evt) => {
            this.handleIncomingAlert(evt);
        });

        socket.on('heatmap_refresh_required', () => {
            if (this.heatmapActive) {
                this.loadHeatmap(document.getElementById('heatmapFilter')?.value || 'all');
            }
        });

        socket.on('crisis_mode_update', (data) => {
            let crisisCtls = document.getElementById('crisisAdditionalControls');
            if (data.active) {
                document.body.classList.add('crisis-mode');
                if(crisisCtls) crisisCtls.style.display = 'flex';
            } else {
                document.body.classList.remove('crisis-mode');
                if(crisisCtls) crisisCtls.style.display = 'none';
            }
        });

        // Initialize state syncing
        fetch('/api/crisis_mode')
            .then(r => r.json())
            .then(data => {
                if (data.active) {
                    document.body.classList.add('crisis-mode');
                    let crisisCtls = document.getElementById('crisisAdditionalControls');
                    if(crisisCtls) crisisCtls.style.display = 'flex';
                }
            })
            .catch(()=>null);

        // Initialize historical seed data over standards REST before WS takes over
        this.fetchAdminComplaints();
        
        if (this.nodes.alertsContainer) {
            this.pollSystemAlerts();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new AdminDashboard();
});
