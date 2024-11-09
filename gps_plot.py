import serial
import time
import folium
import pandas as pd

# Replace with the correct serial port where ESP32 is connected
SERIAL_PORT = '/dev/cu.usbserial-0001'  # e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux/Mac
BAUD_RATE = 9600  # Match this with the ESP32 Serial baud rate

# Open serial connection to ESP32
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow time for the serial connection to initialize

# Data storage for plotting
gps_data = []

# Function to read and parse GPS data
def read_gps_data():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()  # Ignore invalid bytes
            print("Raw data:", line)  # Print for debugging

            # Expected format: LAT,LONG,SPEED,ALT,HDOP,SATS,TIME
            try:
                data = line.split(",")
                if len(data) >= 7:  # Ensure there are enough elements
                    lat = float(data[0])
                    lng = float(data[1])
                    gps_data.append({
                        "Latitude": lat,
                        "Longitude": lng,
                        "Speed": float(data[2]),
                        "Altitude": float(data[3]),
                        "HDOP": float(data[4]),
                        "Satellites": int(data[5]),
                        "Timestamp": data[6]
                    })
                else:
                    print("Data format error: incomplete data")
            except (ValueError, IndexError) as e:
                print("Error parsing line:", e)

            # Collect a limited number of data points for the demo
            if len(gps_data) > 10:  # Arbitrary limit to stop after collecting some data
                break

# Read and parse GPS data
read_gps_data()

# Close the serial connection
ser.close()

# Convert data to DataFrame for easier manipulation
df = pd.DataFrame(gps_data)

# Generate the map centered on the first GPS point
if not df.empty:
    initial_location = [df['Latitude'].iloc[0], df['Longitude'].iloc[0]]
    gps_map = folium.Map(location=initial_location, zoom_start=15)

    # Add points to the map
    for i, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Time: {row['Timestamp']}<br>Speed: {row['Speed']} km/h<br>Altitude: {row['Altitude']} m",
        ).add_to(gps_map)

    # Save the map as an HTML file
    gps_map.save("gps_map.html")
    print("Map saved as gps_map.html")
else:
    print("No GPS data collected.")
