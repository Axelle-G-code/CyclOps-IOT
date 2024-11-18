// Initialize Leaflet Maps for GPS and Weather
const gpsMap = L.map("gpsMap").setView([51.5074, -0.1278], 13); // London
const weatherMap = L.map("weatherMap").setView([51.5074, -0.1278], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    .addTo(gpsMap);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    .addTo(weatherMap);

const routePolyline = L.polyline([], { color: "red" }).addTo(gpsMap);

// Initialize Chart.js for Speed and Rain Coverage
const speedCtx = document.getElementById("speedChart").getContext("2d");
const speedChart = new Chart(speedCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Speed (km/h)",
            data: [],
            fill: false,
            borderColor: "blue",
            tension: 0.1
        }]
    }
});

const rainCtx = document.getElementById("rainChart").getContext("2d");
const rainChart = new Chart(rainCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Rain Coverage (%)",
            data: [],
            fill: false,
            borderColor: "green",
            tension: 0.1
        }]
    }
});

let gpsDevice;
let gpsCharacteristic;
let tracking = false;
let mapCentered = false;

// Fetch Weather Data from API
// Fetch weather data based on latitude and longitude
async function fetchWeatherData(latitude, longitude) {
    const apiKey = "YOUR_API_KEY"; // Replace with your OpenWeatherMap API key

    // Construct the URL for the API call
    const baseUrl = "https://api.openweathermap.org/data/2.5/weather";
    const url = `${baseUrl}?lat=${latitude}&lon=${longitude}` +
                `&units=metric&appid=${apiKey}`;

    try {
        console.log("Fetching weather data from:", url);
        const response = await fetch(url);

        // Check if response is okay
        // Check if response is okay
        if (!response.ok) {
            const errorMessage = "API request failed with status " 
            + response.status;
            console.error(errorMessage);
            return; // Exit the function without throwing
}



        const data = await response.json();
        console.log("Weather data received:", data);

        // Update weather table
        document.getElementById("temp").textContent = `${data.main.temp} °C`;
        document.getElementById("humidity").textContent =
            `${data.main.humidity} %`;
        document.getElementById("windSpeed").textContent =
            `${data.wind.speed} m/s`;
        document.getElementById("rainProb").textContent = data.rain
            ? `${data.rain["1h"] || 0} %`
            : "0 %";

        // Update rain coverage chart
        const timestamp = new Date().toLocaleTimeString();
        rainChart.data.labels.push(timestamp);
        rainChart.data.datasets[0].data.push(data.rain
            ? data.rain["1h"] || 0
            : 0);
        rainChart.update();
    } catch (error) {
        console.error("Error fetching weather data:", error);
    }
}


// Connect to GPS Device
document.getElementById("connectBtn").addEventListener("click", async() => {
    try {
        gpsDevice = await navigator.bluetooth.requestDevice({
            filters: [{ name: "ESP32_GPS" }],
            optionalServices: ["4fafc201-1fb5-459e-8fcc-c5c9c331914b"]
        });

        const server = await gpsDevice.gatt.connect();
        const service = await server.getPrimaryService(
            "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
        );
        gpsCharacteristic = await service.getCharacteristic(
            "beb5483e-36e1-4688-b7f5-ea07361b26a8");

        document.getElementById("startTrackingBtn").disabled = false;
        console.log("Connected to GPS device");

        gpsCharacteristic.startNotifications();
        gpsCharacteristic.addEventListener("characteristicvaluechanged",
            (event) => handleData(event));
    } catch (error) {
        console.error("Bluetooth connection failed", error);
    }
});

// Handle incoming GPS data
function handleData(event) {
    const value = event.target.value;
    const decoder = new TextDecoder("utf-8");
    const data = decoder.decode(value);

    console.log("Raw GPS data received:", data);

    const [latitude, longitude, speed, altitude, hdop, satellites, timestamp] =
        data.split(",");

    console.log("Parsed GPS data:", { latitude, longitude, speed, timestamp });

    if (tracking) {
        updateGPSDisplay(latitude, longitude, speed, timestamp);
        fetchWeatherData(latitude, longitude);
    }
}

function updateGPSDisplay(latitude, longitude, speed, timestamp) {
    const lat = parseFloat(latitude);
    const lng = parseFloat(longitude);

    if (!mapCentered) {
        gpsMap.setView([lat, lng], 13);
        weatherMap.setView([lat, lng], 13);
        mapCentered = true;
    }

    routePolyline.addLatLng([lat, lng]);
    speedChart.data.labels.push(timestamp);
    speedChart.data.datasets[0].data.push(speed);
    speedChart.update();
}
