class AdminDashboard {
    constructor() {
        this.pollRates = {
            stats: 2000,
            complaints: 5000,
            alerts: 4000
        };
        this.chartInstances = {};
        this.alertRegistry = new Set();

        this.domReferences();
        this.initializeCharts();
        this.attachGlobalActions();

        this.startDataLoops();
    }

    domReferences() {
        this.nodes = {
            trafficVal: document.getElementById('trafficVal'),
            aqiVal: document.getElementById('aqiVal'),
            energyVal: document.getElementById('energyVal'),
            alertsContainer: document.getElementById('alertsContainer'),
            complaintBody: document.getElementById('complaintTableBody'),
            actionStatusContainer: document.getElementById('actionStatus'),
            actionStatusText: document.getElementById('actionStatusText')
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

    buildTimeseries(contextId, strokeColor) {
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
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false
                }]
            },
            options: this.getChartConfiguration()
        });
    }

    initializeCharts() {
        this.chartInstances = {
            traffic: this.buildTimeseries('trafficChart', '#1e3a8a'),
            aqi: this.buildTimeseries('aqiChart', '#3b82f6'),
            energy: this.buildTimeseries('energyChart', '#ef4444')
        };
    }

    async syncTelemetry() {
        try {
            const resource = await fetch('/api/dashboard/stats');
            if (!resource.ok) return;

            const metrics = await resource.json();

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
        if (!this.nodes.complaintBody) return;

        try {
            const req = await fetch('/api/complaints');
            if (!req.ok) return;

            const logs = await req.json();

            // Rebuild table DOM
            this.nodes.complaintBody.innerHTML = '';

            logs.forEach(record => {
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
                if (!this.alertRegistry.has(evt.id)) {
                    this.alertRegistry.add(evt.id);

                    let notificationClass = 'alert-info';
                    if (evt.severity === 'Critical') notificationClass = 'alert-critical';
                    if (evt.severity === 'Warning') notificationClass = 'alert-warning';

                    const alertBlock = document.createElement('div');
                    alertBlock.className = `alert-item ${notificationClass} fade-in`;
                    alertBlock.innerHTML = `
                        <div class="alert-header">
                            <span class="alert-title">${evt.severity} - ${evt.type}</span>
                            <span class="alert-time">${new Date(evt.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div class="alert-desc">${evt.desc}</div>
                    `;

                    this.nodes.alertsContainer.prepend(alertBlock);

                    if (this.nodes.alertsContainer.children.length > 5) {
                        this.nodes.alertsContainer.lastElementChild.remove();
                    }
                }
            });
        } catch (err) {
            console.warn('[Alerts] Engine disconnected:', err);
        }
    }

    dispatchProcedure(commandTitle) {
        if (!this.nodes.actionStatusContainer) return;

        this.nodes.actionStatusContainer.style.display = 'block';
        this.nodes.actionStatusContainer.className = 'alert-item alert-critical fade-in';
        this.nodes.actionStatusText.innerHTML = `<strong>Command Sent:</strong> Processing routing directives...`;

        fetch('/api/actions/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: commandTitle })
        })
            .then(res => res.json())
            .then(data => {
                this.nodes.actionStatusContainer.className = 'alert-item alert-info fade-in';
                this.nodes.actionStatusText.innerHTML = `<strong>Execution Complete:</strong> ${data.message || commandTitle}`;
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

    attachGlobalActions() {
        // Expose dispatch to global scope for inline HTML event handlers
        window.simulateAction = this.dispatchProcedure.bind(this);
    }

    startDataLoops() {
        setInterval(() => this.syncTelemetry(), this.pollRates.stats);

        if (this.nodes.complaintBody) {
            setInterval(() => this.fetchAdminComplaints(), this.pollRates.complaints);
            this.fetchAdminComplaints();
        }

        if (this.nodes.alertsContainer) {
            setInterval(() => this.pollSystemAlerts(), this.pollRates.alerts);
            this.pollSystemAlerts();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new AdminDashboard();
});
