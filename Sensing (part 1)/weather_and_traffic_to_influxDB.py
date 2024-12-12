import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
import requests
import schedule
import time
from datetime import datetime, timedelta

#influxdb connection details (token, key and bucket name)
INFLUXDB_TOKEN = "hidden as flagged by Github security"
INFLUXDB_ORG = "hidden as flagged by Github security"
INFLUXDB_BUCKET = "Weather&traffic"
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true&precipitation=true"

# details for TomTom traffic API connection (key and url)
TOMTOM_API_KEY = "hidden as flagged by Github security"
TOMTOM_API_URL = (
    f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key=XQTFC4uflckxoN5swXqDhmrNFTt52TfP&point=51.5014,-0.1419"
)

# initializing influxdb client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
write_api = client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)

# function to write weather and traffic data to InfluxDB
def write_data_to_influxdb():
    try:
        # fetch weather data from Open-Meteo
        weather_response = requests.get(WEATHER_API_URL)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current_weather = weather_data.get("current_weather", {})
        temperature = current_weather.get("temperature")  # Temperature in Celsius
        wind_speed = current_weather.get("windspeed")  # Wind speed in km/h
        precipitation = current_weather.get("precipitation", 0)  # Rainfall in mm (default to 0 if not present)

        # fetch traffic data from TomTom API
        traffic_response = requests.get(TOMTOM_API_URL)
        traffic_response.raise_for_status()
        traffic_data = traffic_response.json()

        # extract relevant traffic data (like current speed, free-flow speed)
        flow_segment_data = traffic_data.get("flowSegmentData", {})
        current_speed = flow_segment_data.get("currentSpeed", 0)  # Speed of traffic in km/h
        free_flow_speed = flow_segment_data.get("freeFlowSpeed", 0)  # Speed under ideal conditions

        # create InfluxDB points
        time_now = datetime.utcnow().isoformat()

        weather_point = (
            Point("weather")
            .tag("location", "London-Westminster")
            .field("temperature", temperature)
            .field("wind_speed", wind_speed)
            .field("precipitation", precipitation)
            .time(time_now, WritePrecision.NS)
        )

        traffic_point = (
            Point("traffic")
            .tag("location", "London-Westminster")
            .field("current_speed", current_speed)
            .field("free_flow_speed", free_flow_speed)
            .time(time_now, WritePrecision.NS)
        )

        # print the data being written to the database
        print(f"Writing to InfluxDB at {time_now}:\n")
        print(f"Weather Data (London - Westminster): Temperature={temperature}°C, Wind Speed={wind_speed} km/h, Precipitation={precipitation} mm")
        print(f"Traffic Data (London - Westminster): Current Speed={current_speed} km/h, Free Flow Speed={free_flow_speed} km/h\n")

        # write points to InfluxDB
        write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, [weather_point, traffic_point])

        print(f"Data successfully written to InfluxDB at {time_now}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# write data to InfluxDB immediately on startup
write_data_to_influxdb()

# schedule data collection every 15 minutes
schedule.every(15).minutes.do(write_data_to_influxdb)

# run the scheduler for 7 days
end_time = datetime.now() + timedelta(days=7)
print("Starting data collection for 7 days...")

try:
    while datetime.now() < end_time:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nData collection interrupted by user.")
finally:
    client.close()
    print("Closed InfluxDB connection.")
