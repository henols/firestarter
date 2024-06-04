#include <Arduino.h>
#include <stdlib.h>
#include <ArduinoJson.h>

#include "firestarter.h"

extern "C"
{
#include "rurp_shield.h"
#include "chip.h"
}
#define RX 0
#define TX 1


// R2 = R1 *  Vout / (Vin - Vout)
// R2 = 44k
// R1 = 270k
// Vin = 21.92v
// Vout = Vin * R2/(R1+R2)
// Vout = 21.92 * 44000÷(44000+270000)
// Vout = 3.071592367


firestarter_handle_t handle;

unsigned long timeout = 0;

void setProgramerMode();
void setComunicationMode();
void resetTimeout();

int allocatreDataBuffer(firestarter_handle_t* handle);
void freeDataBuffer(firestarter_handle_t* handle);

void logInfo(const char* info);
void logError(const char* info);

void setup()
{
  rurp_setup();

  write_to_register(RLSB_LE, 0xF1);
  delay(500);
  write_to_register(RLSB_LE, 0x00);


  setComunicationMode();
  handle.state = STATE_IDLE;
}

void resetTimeout()
{
  timeout = millis() + 1000;
}

void readProm(firestarter_handle_t* handle) {
  if (Serial.available() <= 0) {
    return;
  }

  String s = Serial.readStringUntil('\n');
  if (s != "OK") {
    handle->state = STATE_ERROR;
    return;
  }
  logInfo("Read data");

  if (!allocatreDataBuffer(handle)) {
    return;
  }

  setProgramerMode();
  handle->firestarter_read_data(handle);
  setComunicationMode();

  Serial.print("DATA:  0x");
  Serial.print(handle->address, 16);
  Serial.print(" - 0x");
  Serial.println((handle->address + handle->data_buffer_size), 16);
  Serial.write(handle->data_buffer, handle->data_buffer_size);
  Serial.flush();
  handle->address += handle->data_buffer_size;
  if (handle->address == handle->mem_size)
  {
    Serial.print("OK: Read data from address 0x00 to 0x");
    Serial.println(handle->address, 16);
    Serial.flush();
    handle->state = STATE_DONE;
    return;
  }
  resetTimeout();
}

void eraseProm(firestarter_handle_t* handle) {}

void writeProm(firestarter_handle_t* handle)
{
  if (!allocatreDataBuffer(handle)) {
    return;
  }

  int len;
  while ((len = Serial.readBytes(handle->data_buffer, handle->data_buffer_size)) > 0) {
    if (len < handle->data_buffer_size) {
      logError("Not enough data");
      return;
    }
    if (handle->address + len > handle->mem_size) {
      logError("Address out of range");
      return;
    }
    resetTimeout();

    setProgramerMode();
    handle->firestarter_write_data(handle);
    setComunicationMode();
    if (handle->response_code == RESPONSE_CODE_ERROR) {
      logError(handle->response_msg);
      return;
    }
    Serial.print("OK: Data written, address 0x");
    Serial.println(handle->address, 16);

    Serial.print(" - 0x");
    Serial.println((handle->address + handle->data_buffer_size), 16);

    handle->address += handle->data_buffer_size;

    if (handle->address == handle->mem_size) {
      Serial.println("OK: Memory written");
      Serial.flush();
      handle->state = STATE_DONE;
      return;
    }

    resetTimeout();

  }
}

void readVpp(firestarter_handle_t* handle) {
  if (handle->init) {
    uint8_t ctrl = read_from_register(CTRL_LE);
    write_to_register(CTRL_LE, ctrl | REG_DISABLE);
    handle->init = 0;
    resetTimeout();
  }
  if (Serial.available() <= 0) {
    return;
  }

  String s = Serial.readStringUntil('\n');
  if (s != "OK") {
    handle->state = STATE_ERROR;
    return;
  }

  // delay(100);
  float vpp = get_voltage_average();
  // write_to_register(CTRL_LE, ctrl & ~REG_DISABLE);

  Serial.print("DATA: VPP voltage: ");
  Serial.println(vpp);
  Serial.flush();
  resetTimeout();
}

void setupProm(firestarter_handle_t* handle) {
  if (Serial.available() == 0) {
    return;
  }

  String input = Serial.readStringUntil('\n');
  input.trim();
  if (input.length() == 0) {
    logError("Empty input");
    return;
  }
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, input);
  if (error) {
    Serial.print("ERROR: deserialization error, ");
    Serial.print(error.c_str());
    Serial.print(" input:  ");
    Serial.println(input);
    return;
  }

  handle->init = 1;
  handle->state = (uint8_t)doc["state"];
  if (handle->state < 5) {
    handle->data_buffer_size = DATA_BUFFER_SIZE;
    handle->address = 0;

    // handle->name = doc["name"];
    // handle->manufacturer = doc["manufacturer"];

    handle->mem_type = (uint8_t)doc["type"];
    handle->mem_size = (uint32_t)doc["memory-size"];
    handle->pins = (uint8_t)doc["pin-count"];
    handle->can_erase = (uint32_t)doc["can-erase"];
    handle->has_chip_id = (uint32_t)doc["has-chip-id"];
    handle->chip_id = (uint32_t)doc["chip-id"];
    handle->pulse_delay = (uint32_t)doc["pulse-delay"];

    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.address_lines[0] = 0xFF;

    if (doc.containsKey("bus-config")) {
      logInfo("set up bus-config");
      JsonObject bus_config = doc["bus-config"].as<JsonObject>();

      if (bus_config.containsKey("bus")) {
        copyArray(bus_config["bus"], handle->bus_config.address_lines);
      }
      if (bus_config.containsKey("rw-pin")) {
        handle->bus_config.rw_line = bus_config["rw-pin"];
      }
    }


    int res = configure_chip(handle);
    if (!res) {
      Serial.println("ERROR: Could not configure chip");
      handle->state = STATE_ERROR;
      return;
    }
    Serial.print("INFO: EPROM memory size ");
    Serial.println(handle->mem_size, 10);
  }
  Serial.print("OK: state ");
  Serial.println(handle->state, 10);
  Serial.flush();
  resetTimeout();

}



void loop()
{
  if (handle.state != STATE_IDLE && timeout < millis())
  {
    setProgramerMode();
    write_to_register(RLSB_LE, 0xFF);
    delay(500);
    write_to_register(RLSB_LE, 0x00);

    setComunicationMode();
    logError("Timeout");
    resetTimeout();
    handle.state = STATE_DONE;
  }



  switch (handle.state)
  {
  case STATE_READ:
    readProm(&handle);
    break;
  case STATE_WRITE:
    writeProm(&handle);
    break;
  case STATE_ERASE:
    eraseProm(&handle);
    break;
  case STATE_DONE:
    set_control_pin(ROM_CE, 1);
    set_control_pin(ROM_OE, 1);
    write_to_register(CTRL_LE, 0x00);
    freeDataBuffer(&handle);
    handle.state = STATE_IDLE;
    break;
  case STATE_READ_VPP:
    readVpp(&handle);
    // handle.state = STATE_IDLE;
    break;
  case STATE_ERROR:
    handle.state = STATE_DONE;
    break;
  case STATE_IDLE:
    setupProm(&handle);
    break;

  default:
    Serial.print("ERROR: Unknown state: ");
    Serial.println(handle.state);
    Serial.flush();
    handle.state = STATE_DONE;
    break;
  }
}



void setComunicationMode()
{
  set_control_pin(ROM_CE | ROM_OE, 1);
  DDRD &= ~(0x01);
  Serial.begin(MONITOR_SPEED); // Initialize serial port

  while (!Serial)
  {
    delayMicroseconds(1);
  }
  Serial.flush();
  delay(1);
}

void setProgramerMode()
{
  Serial.end(); // Close serial port
  DDRD |= 0x01;
}

void logInfo(const char* info) {
  Serial.print("INFO: ");
  Serial.println(info);
  Serial.flush();
}

void logError(const char* error) {
  handle.state = STATE_ERROR;
  Serial.print("ERROR: ");
  Serial.println(error);
  Serial.flush();
}

int allocatreDataBuffer(firestarter_handle_t* handle) {
  if (handle->data_buffer == NULL) {
    handle->data_buffer = (byte*)malloc(handle->data_buffer_size);
    if (!handle->data_buffer) {
      logError("Out of memory, creating data_buffer!");
      return 0;
    }
  }
  return 1;
}

void freeDataBuffer(firestarter_handle_t* handle) {
  if (handle->data_buffer) {
    free(handle->data_buffer);
    handle->data_buffer = NULL;
  }
}
