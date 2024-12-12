// esp32 connection and vibration motor control

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// define pins for vibration motors
#define LEFT_MOTOR_PIN 26
#define RIGHT_MOTOR_PIN 27

// define custom service and characteristics uuid
#define SERVICE_UUID "12345678-1234-1234-1234-1234567890ab"
#define NAV_CHAR_UUID "abcd1234-5678-1234-5678-abcdef123456"
#define HAZARD_CHAR_UUID "1234abcd-5678-1234-5678-abcdef654321"

BLEServer *bleServer;
BLECharacteristic *navCharacteristic;
BLECharacteristic *hazardCharacteristic;

// flag to handle connection state
bool deviceConnected = false;

// callback for BLE connection events
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("device connected");
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("device disconnected");
  }
};

void setup() {
  // initialize pins
  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN, OUTPUT);

  // initialize serial communication
  Serial.begin(9600);

  // initialize BLE
  BLEDevice::init("CyclOPS");
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new MyServerCallbacks());

  // create service
  BLEService *service = bleServer->createService(SERVICE_UUID);

  // create characteristics
  navCharacteristic = service->createCharacteristic(
    NAV_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );

  hazardCharacteristic = service->createCharacteristic(
    HAZARD_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );

  // start the service
  service->start();

  // start advertising
  bleServer->getAdvertising()->start();
  Serial.println("waiting for a device to connect...");
}

void loop() {
  if (deviceConnected) {
    // check navigation characteristic for turn instructions
    if (navCharacteristic->getValue().length() > 0) {
      std::string value = navCharacteristic->getValue();
      if (value == "left") {
        analogWrite(LEFT_MOTOR_PIN, 200); // vibrate left motor
        delay(1000);
        analogWrite(LEFT_MOTOR_PIN, 0);
      } else if (value == "right") {
        analogWrite(RIGHT_MOTOR_PIN, 200); // vibrate right motor
        delay(1000);
        analogWrite(RIGHT_MOTOR_PIN, 0);
      }
      navCharacteristic->setValue(""); // clear value
    }

    // check hazard characteristic for hazard alerts
    if (hazardCharacteristic->getValue().length() > 0) {
      std::string value = hazardCharacteristic->getValue();
      if (value == "hazard") {
        analogWrite(LEFT_MOTOR_PIN, 255);
        analogWrite(RIGHT_MOTOR_PIN, 255); // vibrate both motors
        delay(2000);
        analogWrite(LEFT_MOTOR_PIN, 0);
        analogWrite(RIGHT_MOTOR_PIN, 0);
      }
      hazardCharacteristic->setValue(""); // clear value
    }
  }
}
