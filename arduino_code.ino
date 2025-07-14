// Arduino Code for Motion Detection and Security Control

void setup() {
  Serial.begin(9600);        // Start serial communication with Python
  pinMode(2, INPUT);         // PIR Motion Sensor connected to digital pin 2
  pinMode(3, OUTPUT);        // Buzzer or Alarm connected to digital pin 3
  pinMode(4, OUTPUT);        // Door lock control (relay/servo) on digital pin 4
}

void loop() {
  int motionState = digitalRead(2);  // Read the PIR sensor

  if (motionState == HIGH) {
    Serial.println("MOTION_DETECTED"); // Send motion alert to Python
    delay(1000);  // Debounce delay
  }

  // Listen for commands from Python
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');

    if (data == "ALARM_ON") {
      digitalWrite(3, HIGH); // Activate alarm
      delay(5000);           // Alarm duration
      digitalWrite(3, LOW);
    } 
    else if (data == "DOOR_OPEN") {
      digitalWrite(4, HIGH); // Unlock door
      delay(2000);           // Open door for 2 seconds
      digitalWrite(4, LOW);  // Lock again
    }
  }
}
