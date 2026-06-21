#include <Wire.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

#define LCD_ADDR 0x27
#define GREEN_LED 4
#define RED_LED 5
#define BUZZER_PIN 6

struct User {
  byte uid[4];
  const char* name;
};

User knownUsers[] = {
  { { 0x5A, 0x5E, 0xFA, 0x03 }, "Naruto Uzumaki" },
  { { 0xE9, 0x7B, 0xA8, 0x94 }, "Priyanshu Thakur" },
  { { 0x89, 0x6F, 0x5E, 0x93 }, "Milan" },
  { { 0x79, 0xAF, 0xA0, 0x94 }, "Shivam Sharma" },
  { { 0xF9, 0x03, 0x90, 0x54 }, "Suparn" },
  { { 0x69, 0x70, 0x88, 0x54 }, "Ankush Chandel" }
};

const int NUM_USERS = sizeof(knownUsers) / sizeof(knownUsers[0]);

// ---------------- LCD Functions ---------------- //
void i2cSendNibble(uint8_t nibble, uint8_t mode) {
  uint8_t data = (nibble & 0xF0) | 0x08 | mode;
  Wire.beginTransmission(LCD_ADDR);
  Wire.write(data | 0x04);
  Wire.write(data & ~0x04);
  Wire.endTransmission();
}

void i2cSendByte(uint8_t val, uint8_t mode) {
  i2cSendNibble(val & 0xF0, mode);
  i2cSendNibble((val << 4) & 0xF0, mode);
}

void lcdCommand(uint8_t cmd) {
  i2cSendByte(cmd, 0x00);
  delay(2);
}

void lcdData(uint8_t data) {
  i2cSendByte(data, 0x01);
}

void lcdInit() {
  delay(50);
  i2cSendNibble(0x30, 0);
  delay(5);
  i2cSendNibble(0x30, 0);
  delay(5);
  i2cSendNibble(0x30, 0);
  delay(5);
  i2cSendNibble(0x20, 0);
  delay(5);

  lcdCommand(0x28);
  lcdCommand(0x0C);
  lcdCommand(0x06);
  lcdCommand(0x01);
  delay(5);
  lcdSetCursor(0, 0);
}

void lcdSetCursor(uint8_t row, uint8_t col) {
  const uint8_t offsets[] = { 0x00, 0x40 };
  lcdCommand(0x80 | (col + offsets[row]));
}

void lcdPrint(const char* str) {
  int len = 0;
  while (*str && len < 16) {
    lcdData(*str++);
    len++;
  }
  // Fill remaining characters with space
  while (len++ < 16) {
    lcdData(' ');
  }
}
// -------------------------------------------------- //

void beepBuzzerLong() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(1000);
  digitalWrite(BUZZER_PIN, LOW);
}

void beepBuzzerShort() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(300);
  digitalWrite(BUZZER_PIN, LOW);
}

const char* matchUID(byte* uid) {
  for (int i = 0; i < NUM_USERS; i++) {
    bool match = true;
    for (int j = 0; j < 4; j++) {
      if (uid[j] != knownUsers[i].uid[j]) {
        match = false;
        break;
      }
    }
    if (match) return knownUsers[i].name;
  }
  return nullptr;
}

void showUID(byte* uid) {
  Serial.print("Scanned UID: ");
  for (byte i = 0; i < 4; i++) {
    if (uid[i] < 0x10) Serial.print("0");
    Serial.print(uid[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}

// ---------------- Feedback Functions ---------------- //
void successFeedback(const char* name) {
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, HIGH);
  lcdCommand(0x01);
  delay(5);
  lcdSetCursor(0, 0);
  lcdPrint("Access Granted  ");
  lcdSetCursor(1, 0);
  lcdPrint(name);
  beepBuzzerShort();
  delay(1000);
  digitalWrite(GREEN_LED, LOW);
  lcdCommand(0x01);
  delay(5);
}

void deniedFeedback() {
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, HIGH);
  lcdCommand(0x01);
  delay(5);
  lcdSetCursor(0, 0);
  lcdPrint("Access Denied   ");
  lcdSetCursor(1, 0);
  lcdPrint("Unknown Card    ");
  beepBuzzerLong();
  delay(1000);
  digitalWrite(RED_LED, LOW);
  lcdCommand(0x01);
  delay(5);
}
// -------------------------------------------------- //

void setup() {
  Serial.begin(9600);
  Wire.begin();
  SPI.begin();
  rfid.PCD_Init();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  lcdInit();
  lcdSetCursor(0, 0);
  lcdPrint("Scan Your Card  ");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  byte* scannedUID = rfid.uid.uidByte;
  showUID(scannedUID);

  lcdCommand(0x01);
  delay(5);
  lcdSetCursor(0, 0);
  lcdPrint("Card Detected   ");

  const char* userName = matchUID(scannedUID);
  if (userName != nullptr) {
    successFeedback(userName);
  } else {
    deniedFeedback();
  }

  lcdSetCursor(0, 0);
  lcdPrint("Scan Next Card  ");

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
