// Initialize Leaflet Map
const map = L.map("map").setView([51.5074, -0.1278], 13); // set map on London automatically
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
const routePolyline = L.polyline([], { color: 'red' }).addTo(map);

// Initialize Chart.js Speed Graph
const ctx = document.getElementById('chart').getContext('2d');
const speedChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Timestamps
        datasets: [{
            label: 'Speed (km/h)',
            data: [],
            fill: false,
            borderColor: 'blue',
            tension: 0.1
        }]
    }
});

let gpsDevice;
let gpsCharacteristic;
let gpsData = [];
let tracking = false;
let mapCentered = false;

// Connect to Bluetooth Device
document.getElementById("connectBtn").addEventListener("click", async () => {
    try {
        gpsDevice = await navigator.bluetooth.requestDevice({
            filters: [{ name: "ESP32_GPS" }],
            optionalServices: ["4fafc201-1fb5-459e-8fcc-c5c9c331914b"] // Replace with your GPS service UUID
        });

        const server = await gpsDevice.gatt.connect();
        const service = await server.getPrimaryService("4fafc201-1fb5-459e-8fcc-c5c9c331914b");
        gpsCharacteristic = await service.getCharacteristic("beb5483e-36e1-4688-b7f5-ea07361b26a8"); // Replace with your GPS characteristic UUID

        document.getElementById("startTrackingBtn").disabled = false;
        console.log("Connected to GPS device");

        gpsCharacteristic.startNotifications();
        gpsCharacteristic.addEventListener("characteristicvaluechanged", handleData);
    } catch (error) {
        console.error("Bluetooth connection failed", error);
    }
});

// Handle incoming data and debug with console.log()
function handleData(event) {
    const value = event.target.value;
    const decoder = new TextDecoder("utf-8");
    const data = decoder.decode(value);
    
    console.log("Raw GPS data received:", data); // Log raw data

    const [latitude, longitude, speed, altitude, hdop, satellites, timestamp] = data.split(",");

    if (tracking) {
        console.log("Parsed GPS data:", { latitude, longitude, speed, timestamp }); // Log parsed data

        gpsData.push({ latitude: parseFloat(latitude), longitude: parseFloat(longitude), speed: parseFloat(speed), timestamp });
        updateMapAndGraph(latitude, longitude, speed, timestamp);
    }
}

// Start Tracking Button
document.getElementById("startTrackingBtn").addEventListener("click", () => {
    tracking = true;
    gpsData = [];
    console.log("Tracking started");
    document.getElementById("stopTrackingBtn").disabled = false;
});

// Stop Tracking Button
document.getElementById("stopTrackingBtn").addEventListener("click", () => {
    tracking = false;
    console.log("Tracking stopped");
    document.getElementById("stopTrackingBtn").disabled = true;
});

// Update Map and Graph with New Data
function updateMapAndGraph(latitude, longitude, speed, timestamp) {
    const lat = parseFloat(latitude);
    const lng = parseFloat(longitude);

    // Center the map only the first time data is received
    if (!mapCentered) {
        map.setView([lat, lng], 13); // 13 is the zoom level
        mapCentered = true;
        console.log("Map centered at:", { lat, lng });
    }

    // Add the new point to the map route
    routePolyline.addLatLng([lat, lng]);

    // Update Chart.js graph with new speed data
    speedChart.data.labels.push(timestamp);
    speedChart.data.datasets[0].data.push(speed);
    speedChart.update();

    console.log("Updated map and chart with:", { lat, lng, speed, timestamp });
}
