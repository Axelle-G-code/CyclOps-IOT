#include <BluetoothSerial.h>

// Define pins for vibration motors
#define LEFT_MOTOR_PIN 25
#define RIGHT_MOTOR_PIN 26

// Bluetooth Serial instance
BluetoothSerial SerialBT;

// State variables
String current_direction;

// Setup function
void setup() {
  // Initialize serial communication for debugging
  Serial.begin(115200);

  // Initialize Bluetooth with the name "ESP32_Bike_Nav"
  SerialBT.begin("ESP32_Bike_Nav");

  // Initialize motor pins as outputs
  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN, OUTPUT);

  // Ensure motors are initially off
  digitalWrite(LEFT_MOTOR_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_PIN, LOW);

  Serial.println("ESP32 is ready and waiting for directions...");
}

// Loop function
void loop() {
  // Check for incoming Bluetooth messages
  if (SerialBT.available()) {
    current_direction = SerialBT.readString();  // Read the direction command
    handleDirection(current_direction);         // Handle the direction
  }
}

// Function to handle the received direction command
void handleDirection(String direction) {
  direction.trim();  // Remove any trailing or leading whitespace
  
  if (direction == "LEFT") {
    Serial.println("Turning left...");
    vibrateMotor(LEFT_MOTOR_PIN, 100);  // Short vibration before turn
    delay(500);
    vibrateMotor(LEFT_MOTOR_PIN, 300);  // Long vibration at the turn
  } 
  else if (direction == "RIGHT") {
    Serial.println("Turning right...");
    vibrateMotor(RIGHT_MOTOR_PIN, 100); // Short vibration before turn
    delay(500);
    vibrateMotor(RIGHT_MOTOR_PIN, 300); // Long vibration at the turn
  } 
  else if (direction == "WARNING") {
    Serial.println("Warning: High congestion zone detected");
    // Vibrate both motors twice to indicate high congestion
    vibrateMotor(LEFT_MOTOR_PIN, 200);
    delay(200);
    vibrateMotor(RIGHT_MOTOR_PIN, 200);
    delay(200);
    vibrateMotor(LEFT_MOTOR_PIN, 200);
    delay(200);
    vibrateMotor(RIGHT_MOTOR_PIN, 200);
  } 
  else {
    Serial.println("Unknown command: " + direction);
  }
}

// Function to vibrate a motor for a specific duration
void vibrateMotor(int motor_pin, int duration) {
  digitalWrite(motor_pin, HIGH);  // Turn motor on
  delay(duration);                // Wait for the specified duration
  digitalWrite(motor_pin, LOW);   // Turn motor off
}
