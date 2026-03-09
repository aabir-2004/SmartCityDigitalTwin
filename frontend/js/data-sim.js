/**
 * data-sim.js
 * Simulates data layers, providing mocked local responses while true
 * backend endpoints are yet to be integrated.
 */

const STORAGE_KEY_COMPLAINTS = "smartcity_complaints";
const STORAGE_KEY_ALERTS = "smartcity_alerts";

// Seed some initial complaints if none exist
if (!localStorage.getItem(STORAGE_KEY_COMPLAINTS)) {
  const seedComplaints = [
    {
      id: "CMP-" + Math.floor(Math.random() * 10000),
      category: "Traffic",
      location: "Sector 3 Junction",
      description: "Severe traffic loop causing 45 min delays.",
      status: "Open",
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString() // 30 mins ago
    },
    {
      id: "CMP-" + Math.floor(Math.random() * 10000),
      category: "Infrastructure",
      location: "East Side Highway",
      description: "Street lights completely off on the main highway bridge.",
      status: "In Progress",
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString()
    }
  ];
  localStorage.setItem(STORAGE_KEY_COMPLAINTS, JSON.stringify(seedComplaints));
}

// Global helper to generate mock complaints
window.saveComplaint = function (complaintObj) {
  let complaints = JSON.parse(localStorage.getItem(STORAGE_KEY_COMPLAINTS) || "[]");
  complaintObj.id = "CMP-" + Math.floor(Math.random() * 10000);
  complaintObj.status = "Open";
  complaintObj.timestamp = new Date().toISOString();
  complaints.unshift(complaintObj); // add to top
  localStorage.setItem(STORAGE_KEY_COMPLAINTS, JSON.stringify(complaints));
  return true;
};

// Global helper to fetch complaints
window.getComplaints = function () {
  return JSON.parse(localStorage.getItem(STORAGE_KEY_COMPLAINTS) || "[]");
};

// Generate mock IoT live stats
window.getMockIoTStats = function() {
  return {
    traffic: Math.floor(Math.random() * 40) + 60,   // 60 - 100 avg index
    airQuality: Math.floor(Math.random() * 150) + 50, // 50 - 200 AQI
    energyUsage: (Math.random() * 5 + 40).toFixed(1), // 40 - 45 MW
  };
};

window.generateRandomAlert = function() {
  const types = [
    { type: "Traffic Spike", severity: "Warning", desc: "Unusual congestion detected." },
    { type: "Pollution Alert", severity: "Critical", desc: "AQI spiked past 180." },
    { type: "Energy Grid", severity: "Info", desc: "Load balancing active." }
  ];
  const choice = types[Math.floor(Math.random() * types.length)];
  return {
    id: "ALT-" + Math.floor(Math.random() * 10000),
    type: choice.type,
    severity: choice.severity,
    desc: choice.desc,
    timestamp: new Date().toISOString()
  };
};
