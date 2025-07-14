#include <SoftwareSerial.h>
#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9
#define SS_PIN 10
MFRC522 rfid(SS_PIN, RST_PIN);

String authorizedUID = "12AB34CD";

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  pinMode(2, INPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
}

void loop() {
  int motion = digitalRead(2);
  if (motion == HIGH) {
    Serial.println("MOTION_DETECTED");
    delay(1000);
  }

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();

    if (uid == authorizedUID) {
      Serial.println("DOOR_OPEN");
      digitalWrite(4, HIGH);
      delay(2000);
      digitalWrite(4, LOW);
    }
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    if (cmd == "ALARM_ON") {
      digitalWrite(3, HIGH);
      delay(5000);
      digitalWrite(3, LOW);
    } else if (cmd == "DOOR_OPEN") {
      digitalWrite(4, HIGH);
      delay(2000);
      digitalWrite(4, LOW);
    }
  }
}
