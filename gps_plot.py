import serial
import time
import folium
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic

# Replace with your ESP32’s serial port
SERIAL_PORT = '/dev/cu.usbserial-0001'
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow serial connection to initialize

gps_data = []
tracking = False  # Start tracking only after moving 10 meters + buffer
last_location = None
stopped_time = None
MOVEMENT_THRESHOLD = 15  # 15 meters as a buffer to account for GPS drift

# Function to create map and save it as HTML
def create_map(gps_data):
    if not gps_data:  # Check if gps_data is empty
        print("No GPS data to plot.")
        return
    
    start_location = [gps_data[0]['Latitude'], gps_data[0]['Longitude']]
    journey_map = folium.Map(location=start_location, zoom_start=15)
    
    # Plot each point and add a red line for the journey
    coordinates = [(data['Latitude'], data['Longitude']) for data in gps_data]
    folium.PolyLine(coordinates, color="red", weight=2.5, opacity=1).add_to(journey_map)
    
    # Save map to HTML
    journey_map.save("journey_map.html")
    print("Map saved as journey_map.html")

# Function to create a speed graph and save it as an image
def create_speed_graph(gps_data):
    if not gps_data:  # Check if gps_data is empty
        print("No GPS data to plot.")
        return
    
    times = [data['Timestamp'] for data in gps_data]
    speeds = [data['Speed'] for data in gps_data]
    
    plt.figure(figsize=(10, 5))
    plt.plot(times, speeds, marker='o')
    plt.title("Speed over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Speed (km/h)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("speed_graph.png")
    plt.close()
    print("Speed graph saved as speed_graph.png")

# Function to read and track GPS data
def read_and_track_gps():
    global last_location, stopped_time, tracking

    # Define the start time for a 1-hour run duration
    start_time = time.time()
    max_duration = 3600  # Run for 1 hour (3600 seconds)
    tracking_stopped = False  # Flag to indicate if tracking has stopped due to inactivity

    while True:
        # Check if the maximum duration has passed
        if time.time() - start_time > max_duration:
            print("Reached maximum run time of 1 hour.")
            break

        try:
            # Check for available data in serial buffer
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(line)  # For debugging

                try:
                    # Check if line contains 7 values to match the GPS data format
                    data = line.split(",")
                    if len(data) != 7:
                        raise ValueError("Invalid data format")  # Skip lines that aren't in the expected format
                    
                    # Parse the data fields
                    lat = float(data[0])
                    lng = float(data[1])
                    speed = float(data[2])
                    altitude = float(data[3])
                    hdop = float(data[4])
                    satellites = int(data[5])
                    timestamp = data[6]

                    # Record GPS data
                    current_location = (lat, lng)
                    current_time = time.time()

                    if last_location:
                        distance_moved = geodesic(last_location, current_location).meters
                        if not tracking:
                            # Start tracking if movement exceeds MOVEMENT_THRESHOLD
                            if distance_moved > MOVEMENT_THRESHOLD:
                                tracking = True
                                tracking_stopped = False  # Reset tracking stopped flag
                                gps_data.append({
                                    "Latitude": lat,
                                    "Longitude": lng,
                                    "Speed": speed,
                                    "Altitude": altitude,
                                    "HDOP": hdop,
                                    "Satellites": satellites,
                                    "Timestamp": timestamp
                                })
                                last_location = current_location
                                print(f"Tracking started; moved {distance_moved:.2f} meters.")
                        else:
                            # Continue logging if already tracking
                            gps_data.append({
                                "Latitude": lat,
                                "Longitude": lng,
                                "Speed": speed,
                                "Altitude": altitude,
                                "HDOP": hdop,
                                "Satellites": satellites,
                                "Timestamp": timestamp
                            })
                            last_location = current_location

                            # Check if GPS has been stationary for 5 minutes
                            if distance_moved < 10:
                                if stopped_time is None:
                                    stopped_time = current_time
                                elif current_time - stopped_time > 300:  # 5 minutes in seconds
                                    print("GPS stopped moving for 5 minutes.")
                                    tracking = False
                                    tracking_stopped = True  # Set tracking stopped flag
                            else:
                                stopped_time = None  # Reset stopped timer if movement is detected
                    else:
                        # Set initial location without logging
                        last_location = current_location

                except (ValueError, IndexError) as e:
                    print("Error parsing line:", e)

        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break  # Exit loop if serial port becomes unavailable
        
        # After tracking has stopped due to inactivity, continue loop but don't log data
        if tracking_stopped:
            continue

    # After tracking ends (1 hour), create map and speed graph if data is present
    if gps_data:
        create_map(gps_data)
        create_speed_graph(gps_data)
    else:
        print("No GPS data to plot.")

# Run the GPS tracking function
read_and_track_gps()
ser.close()
