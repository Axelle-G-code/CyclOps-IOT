let map;
let directionsService;
let directionsRenderer;
let esp32Device;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 51.5074, lng: -0.1278 }, // Center on London
        zoom: 13,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
    });
}

async function connectToESP32() {
    try {
        esp32Device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
        });
        await esp32Device.gatt.connect();
        document.getElementById("esp32-status").textContent = "ESP32 Connected";
    } catch (error) {
        alert("Failed to connect to ESP32. Please try again.");
    }
}

async function startJourney() {
    const startPoint = document.getElementById("start-point").value;
    const endPoint = document.getElementById("end-point").value;

    if (!startPoint || !endPoint) {
        alert("Please enter both start and end points.");
        return;
    }

    try {
        const response = await fetch("/api/get-directions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ start: startPoint, end: endPoint }),
        });

        if (!response.ok) throw new Error("Failed to fetch directions");

        const directions = await response.json();
        directionsRenderer.setDirections(directions);

        updateGraphData();
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function updateGraphData() {
    try {
        const response = await fetch("/api/get-weather-congestion");

        if (!response.ok) throw new Error("Failed to fetch congestion data");

        const data = await response.json();
        renderCongestionGraph(data);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function renderCongestionGraph(data) {
    const ctx = document.getElementById("congestionGraph").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Speed (km/h)",
                data: data.speeds,
                borderColor: "#3e95cd",
                fill: false,
            }],
        },
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initMap();

    document.getElementById("esp32-button").addEventListener("click", connectToESP32);
    document.getElementById("start-journey-button").addEventListener("click", startJourney);
});
