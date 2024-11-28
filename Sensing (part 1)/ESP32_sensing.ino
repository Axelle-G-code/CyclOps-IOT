#if defined(ESP32)
#include <WiFiMulti.h>
WiFiMulti wifiMulti;
#define DEVICE "ESP32"
#elif defined(ESP8266)
#include <ESP8266WiFiMulti.h>
ESP8266WiFiMulti wifiMulti;
#define DEVICE "ESP8266"
#endif

#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>
#include <TinyGPS++.h>

// Custom Ultrasonic Sensor Implementation
#define TRIGGER_PIN 5
#define ECHO_PIN 18

// WiFi Credentials
#define WIFI_SSID "Pixel_1743"
#define WIFI_PASSWORD "doudou123"

// InfluxDB Configuration
#define INFLUXDB_URL "https://us-east-1-1.aws.cloud2.influxdata.com"
#define INFLUXDB_TOKEN "2jRrp5qcV2fAy-T4c8J8pp9JuP9UKEvQOnq1HPvoFDOQO938RIPfDaXRv1cG_RV56ii6O_AZHOGrC7G94qu9-w=="
#define INFLUXDB_ORG "eaa5d7ece23e8f9d"
#define INFLUXDB_BUCKET "IOT data"

// Time zone info
#define TZ_INFO "UTC0"

// Declare InfluxDB client instance with preconfigured InfluxCloud certificate
InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);

// Declare Data Points
Point gpsPoint("gps_data");
Point proximityPoint("proximity_data");

// GPS Setup
TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // Use UART1 for GPS

// Function to Setup Ultrasonic Sensor
void setupUltrasonic() {
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

// Function to Get Distance from Ultrasonic Sensor
float getDistance() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2; // Convert to cm
  return distance;
}

// Function to Connect to Wi-Fi
void connectToWiFi() {
  wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (wifiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }
  Serial.println("\nWi-Fi connected.");
}

// Function to Setup InfluxDB
void setupInfluxDB() {
  timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");
  if (client.validateConnection()) {
    Serial.print("Connected to InfluxDB: ");
    Serial.println(client.getServerUrl());
  } else {
    Serial.print("InfluxDB connection failed: ");
    Serial.println(client.getLastErrorMessage());
  }
}

// Function to Publish GPS Data
void publishGPSData(double lat, double lon, double speed) {
  gpsPoint.clearFields();
  gpsPoint.addField("latitude", lat);
  gpsPoint.addField("longitude", lon);
  gpsPoint.addField("speed", speed);

  if (!client.writePoint(gpsPoint)) {
    Serial.print("Failed to write GPS data: ");
    Serial.println(client.getLastErrorMessage());
  } else {
    Serial.println("GPS data published.");
  }
}

// Function to Publish Proximity Data
void publishProximityData(float distance) {
  proximityPoint.clearFields();
  proximityPoint.addField("distance", distance);

  if (!client.writePoint(proximityPoint)) {
    Serial.print("Failed to write proximity data: ");
    Serial.println(client.getLastErrorMessage());
  } else {
    Serial.println("Proximity data published.");
  }
}

// Function to Collect and Log Data
void collectAndLogData() {
  // Read GPS Data
  double lat = gps.location.lat();
  double lon = gps.location.lng();
  double speed = gps.speed.kmph();

  // Read Ultrasonic Sensor Data
  float distance = getDistance();

  // Log GPS Data to Serial
  if (gps.location.isValid()) {
    Serial.print("GPS Data - Latitude: ");
    Serial.print(lat, 6);
    Serial.print(", Longitude: ");
    Serial.print(lon, 6);
    Serial.print(", Speed: ");
    Serial.print(speed);
    Serial.println(" km/h");
  } else {
    Serial.println("GPS Data - No valid GPS fix.");
  }

  // Log Proximity Sensor Data to Serial
  Serial.print("Proximity Data - Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Publish Data to InfluxDB
  if (gps.location.isValid()) {
    publishGPSData(lat, lon, speed);
  }
  publishProximityData(distance);
}

void setup() {
  Serial.begin(9600);
  gpsSerial.begin(9600, SERIAL_8N1, 17, 16); // Initialize GPS (RX=17, TX=16)
  setupUltrasonic();                         // Initialize Ultrasonic Sensor
  connectToWiFi();                           // Connect to Wi-Fi
  setupInfluxDB();                           // Setup InfluxDB

  // Add tags to the data points
  gpsPoint.addTag("device", DEVICE);
  gpsPoint.addTag("SSID", WiFi.SSID());

  proximityPoint.addTag("device", DEVICE);
  proximityPoint.addTag("SSID", WiFi.SSID());
}

void loop() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read()); // Parse GPS data
  }
  collectAndLogData();            // Collect, log, and publish data
  delay(1000);                    // Wait 1 second before next cycle
}