#include "version.h"
#include "firestarter.h"
#include "oled.h"
#include "SSD1306Ascii.h"
#include "SSD1306AsciiAvrI2c.h"

// 0X3C+SA0 - 0x3C or 0x3D
#define I2C_ADDRESS 0x3C

SSD1306AsciiAvrI2c oled;
uint8_t prevOledCmd = 255; //CMD_IDLE;
const unsigned long OLED_TIMEOUT = 30000; // 30 seconds
unsigned long oledLastActivityTime = 0;
bool oledIsOn = false;
bool oledSplash = false;

void oledInit() {
  //Wire.begin();
  //Wire.setClock(400000L);

  oled.begin(&Adafruit128x64, I2C_ADDRESS);
  oled.setFont(Adafruit5x7);
  //oled.setScrollMode(SCROLL_MODE_AUTO);
  oledActivity();
}

void oledSplashScreen() {
  oled.clear();
  oled.setCursor(0, 0); // will overwrite content, so the screen will not be blinking?
  oled.set2X();
  oled.println("Firestarter");
  oled.set1X();
  oledDisplayFirmwareVersion();
  oled.println();
  oledActivity();
}

void oledDisplayFirmwareVersion() {
  oled.print("Ver:");
  oled.print(FW_VERSION);
  oled.print("-");
  oled.println(rurp_get_physical_hardware_revision());
}

void oledDisplayMessage(const char* message) {
  //oled.clear();
  oled.setCursor(0, 5);
  oled.println(message);
}


void oledRefresh(uint8_t cmd) {
  if (!oledSplash) {
    oledSplashScreen();
    oledSplash = true;
  }
  if (prevOledCmd != cmd) {
    oledActivity();
    prevOledCmd = cmd;
    switch (cmd) {
      case CMD_READ:
          oledDisplayMessage("Reading...");
          break;
      case CMD_WRITE:
          oledDisplayMessage("Writing...");
          break;
      case CMD_VERIFY:
          oledDisplayMessage("Verifying...");
          break;
      case CMD_ERASE:
          oledDisplayMessage("Erasing...");
          break;
      case CMD_BLANK_CHECK:
          oledDisplayMessage("Checking blank status...");
          break;
      case CMD_CHECK_CHIP_ID:
          oledDisplayMessage("Checking chip ID...");
          break;
      case CMD_SDP_UNLOCK:
          oledDisplayMessage("Unlocking SDP...");
          break;
      case CMD_SDP_LOCK:
          oledDisplayMessage("Locking SDP...");
          break;
      case CMD_LOCK_STATUS:
          oledDisplayMessage("Checking lock status...");
          break;
      case CMD_READ_VPP:
      case CMD_READ_VPE:
          oledDisplayMessage("Reading voltage...");
          break;
      case CMD_IDLE:
          oledDisplayMessage("Idle                       ");
          break;
      case CMD_FW_VERSION:
          oledDisplayMessage("Getting firmware version...");
          break;
      case CMD_CONFIG:
          oledDisplayMessage("Getting configuration...");
          break;
      default:
          break;
    }
  }
  // protect oled from burning
  if ((millis() - oledLastActivityTime >= OLED_TIMEOUT) && oledIsOn) {
    //oled.ssd1306WriteCmd(SSD1306_DISPLAYOFF); // turn off
    oledIsOn = false;
  }
}

void oledActivity() {
  oledLastActivityTime = millis();
  if (!oledIsOn) {
    //oled.ssd1306WriteCmd(SSD1306_DISPLAYON);
    oledIsOn = true;
  }
}