let map, directionsLayer, startMarker, endMarker;
let bluetoothDevice;
let gattServer;
let characteristic;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize map
  map = L.map("map").setView([51.505, -0.09], 13);

  // Add map layer from OpenStreetMap
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Layer for directions
  directionsLayer = L.layerGroup().addTo(map);
});

async function connectBluetooth() {
  try {
    bluetoothDevice = await navigator.bluetooth.requestDevice({
      filters: [{ name: "ESP32_Bike_Nav" }],
    });
    gattServer = await bluetoothDevice.gatt.connect();
    document.getElementById("status").innerText = "Connected";
  } catch (error) {
    console.error("Connection failed!", error);
    alert("Connection failed: " + error.message);
  }
}

function fetchSuggestions(inputId) {
  const input = document.getElementById(inputId).value;
  if (input.length < 3) return;

  fetch(`https://nominatim.openstreetmap.org/search?format=json&countrycodes=GB&q=${input}`)
    .then((response) => response.json())
    .then((data) => {
      const suggestionList = document.getElementById(`${inputId}-suggestions`);
      suggestionList.innerHTML = "";

      data.forEach((place) => {
        const listItem = document.createElement("li");
        listItem.textContent = place.display_name;
        listItem.addEventListener("click", () => {
          document.getElementById(inputId).value = place.display_name;
          suggestionList.innerHTML = "";
        });
        suggestionList.appendChild(listItem);
      });
    })
    .catch((error) => console.error("Error fetching suggestions:", error));
}

function sendDirection(direction) {
  if (characteristic) {
    let encoder = new TextEncoder();
    characteristic.writeValue(encoder.encode(direction));
  } else {
    alert("No Bluetooth characteristic available to send data.");
  }
}

function getDirections() {
  const startLocation = document.getElementById("start").value;
  const endLocation = document.getElementById("end").value;

  if (!startLocation || !endLocation) {
    alert("Please enter both start and end locations.");
    return;
  }

  // Clear previous markers and directions
  directionsLayer.clearLayers();
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);

  // Fetch start and end locations
  fetch(`https://nominatim.openstreetmap.org/search?format=json&countrycodes=GB&q=${startLocation}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.length > 0) {
        const startCoords = [data[0].lat, data[0].lon];
        startMarker = L.marker(startCoords).addTo(map).bindPopup("Start").openPopup();
        map.setView(startCoords, 13);

        return fetch(`https://nominatim.openstreetmap.org/search?format=json&countrycodes=GB&q=${endLocation}`);
      } else {
        throw new Error("Start location not found");
      }
    })
    .then((response) => response.json())
    .then((data) => {
      if (data.length > 0) {
        const endCoords = [data[0].lat, data[0].lon];
        endMarker = L.marker(endCoords).addTo(map).bindPopup("End").openPopup();

        // Use OpenRouteService API to get directions
        const apiKey = "5b3ce3597851110001cf62486f130823a88f456baf26358870d167a9";
        fetch(
          `https://api.openrouteservice.org/v2/directions/foot-walking?api_key=${apiKey}&start=${startMarker.getLatLng().lng},${startMarker.getLatLng().lat}&end=${endMarker.getLatLng().lng},${endMarker.getLatLng().lat}`
        )
          .then((response) => response.json())
          .then((routeData) => {
            const coordinates = routeData.features[0].geometry.coordinates.map((coord) => [coord[1], coord[0]]);
            L.polyline(coordinates, { color: "blue" }).addTo(directionsLayer);

            // Example to send direction to ESP32
            sendDirection("LEFT");
          })
          .catch((error) => {
            console.error("Error fetching directions:", error);
            alert("Could not find directions. Please try again.");
          });
      } else {
        throw new Error("End location not found");
      }
    })
    .catch((error) => {
      console.error("Error fetching locations:", error);
      alert("Could not find locations. Please try again.");
    });
}
