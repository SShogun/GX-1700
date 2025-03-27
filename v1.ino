#include <SoftwareSerial.h>
// Define motor control pins for the two channels
// These pins are connected to the L293D shield outputs controlling the motors.
// For example, left motors are controlled by two pins and right motors by two pins.
const int leftMotorForward  = 3;
const int leftMotorBackward = 4;
const int rightMotorForward = 5;
const int rightMotorBackward= 6;

void setup() {
  // Initialize serial communication (HC-05 is connected via Arduino's Serial)
  Serial.begin(9600);
  
  // Initialize motor pins as outputs
  pinMode(leftMotorForward, OUTPUT);
  pinMode(leftMotorBackward, OUTPUT);
  pinMode(rightMotorForward, OUTPUT);
  pinMode(rightMotorBackward, OUTPUT);
  
  // Stop all motors initially
  stopMotors();
}

void loop() {
  // Check if a serial command is available
  if (Serial.available() > 0) {
    char command = Serial.read();
    Serial.print("Received command: ");
    Serial.println(command);
    executeCommand(command);
  }
}

// Execute command based on the character received
void executeCommand(char cmd) {
  switch (cmd) {
    case 'F': // Forward
      forward();
      break;
    case 'B': // Backward
      backward();
      break;
    case 'L': // Turn left
      turnLeft();
      break;
    case 'R': // Turn right
      turnRight();
      break;
    case 'S': // Stop
      stopMotors();
      break;
    default:
      // For any unknown command, stop the robot.
      stopMotors();
      break;
  }
}

// Drive both motor groups forward
void forward() {
  digitalWrite(leftMotorForward, HIGH);
  digitalWrite(leftMotorBackward, LOW);
  digitalWrite(rightMotorForward, HIGH);
  digitalWrite(rightMotorBackward, LOW);
}

// Drive both motor groups backward
void backward() {
  digitalWrite(leftMotorForward, LOW);
  digitalWrite(leftMotorBackward, HIGH);
  digitalWrite(rightMotorForward, LOW);
  digitalWrite(rightMotorBackward, HIGH);
}

// Turn left: Stop left motors, run right motors forward
void turnLeft() {
  digitalWrite(leftMotorForward, LOW);
  digitalWrite(leftMotorBackward, LOW);
  digitalWrite(rightMotorForward, HIGH);
  digitalWrite(rightMotorBackward, LOW);
}

// Turn right: Run left motors forward, stop right motors
void turnRight() {
  digitalWrite(leftMotorForward, HIGH);
  digitalWrite(leftMotorBackward, LOW);
  digitalWrite(rightMotorForward, LOW);
  digitalWrite(rightMotorBackward, LOW);
}

// Stop all motors
void stopMotors() {
  digitalWrite(leftMotorForward, LOW);
  digitalWrite(leftMotorBackward, LOW);
  digitalWrite(rightMotorForward, LOW);
  digitalWrite(rightMotorBackward, LOW);
}
