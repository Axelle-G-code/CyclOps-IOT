import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

# Key configurations
API_KEY = "your_openweathermap_api_key"  # Replace with your OpenWeatherMap API key
CITY = "Westminster,London,GB"  # Location for weather data
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "2jRrp5qcV2fAy-T4c8J8pp9JuP9UKEvQOnq1HPvoFDOQO938RIPfDaXRv1cG_RV56ii6O_AZHOGrC7G94qu9-w=="
INFLUXDB_ORG = "eaa5d7ece23e8f9d"
INFLUXDB_BUCKET = "IOT data"

def fetch_weather():
    """
    Fetch current weather data for the specified city using OpenWeatherMap API.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
        }
        print(f"Weather data fetched: {weather}")
        return weather
    else:
        print(f"Failed to fetch weather data: {response.status_code} - {response.text}")
        return None

def publish_to_influxdb(weather):
    """
    Publish weather data to InfluxDB.
    """
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=WritePrecision.NS)

        point = Point("weather") \
            .tag("location", CITY) \
            .field("temperature", weather["temperature"]) \
            .field("humidity", weather["humidity"]) \
            .field("pressure", weather["pressure"]) \
            .field("wind_speed", weather["wind_speed"]) \
            .field("description", weather["description"]) \
            .time(datetime.utcnow(), WritePrecision.NS)

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print("Weather data published to InfluxDB.")

if __name__ == "__main__":
    # Fetch weather data
    weather = fetch_weather()

    if weather:
        # Publish data to InfluxDB
        publish_to_influxdb(weather)
