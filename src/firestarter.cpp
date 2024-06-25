/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "firestarter.h"
#include <Arduino.h>
#include <stdlib.h>

#include "json_parser.h"
 // #include "jsmn.h"
#include "rurp_shield.h"
#include "memory.h"
#include "version.h"



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
jsmntok_t tokens[NUMBER_JSNM_TOKENS];

void setProgramerMode();
void setComunicationMode();
void resetTimeout();

void logInfo(const char* info);
void logError(const char* info);

void setup() {
  rurp_setup();
  setComunicationMode();
  handle.state = STATE_IDLE;
}

void resetTimeout()
{
  timeout = millis() + 1000;
}

int waitCheckForOK(){
  if (Serial.available() < 2) {
    return 0;
  }
  if(Serial.read()!= 'O' || Serial.read() != 'K' ){
    logInfo("Expecting OK");
    resetTimeout();
    return 0 ;
  }
  return 1;
}

void readProm(firestarter_handle_t* handle) {
  if (!waitCheckForOK()) {
    return;
  }

  setProgramerMode();
  handle->firestarter_read_data(handle);
  setComunicationMode();

  Serial.print("DATA:  0x");
  Serial.print(handle->address, 16);
  Serial.print(" - 0x");
  Serial.println((handle->address + DATA_BUFFER_SIZE), 16);
  Serial.write(handle->data_buffer, DATA_BUFFER_SIZE);
  Serial.flush();
  handle->address += DATA_BUFFER_SIZE;
  if (handle->address == handle->mem_size) {
    Serial.print("OK: Read data from address 0x00 to 0x");
    Serial.println(handle->address, 16);
    Serial.flush();
    handle->state = STATE_DONE;
    return;
  }
  resetTimeout();
}


void eraseProm(firestarter_handle_t* handle) {}

void writeProm(firestarter_handle_t* handle) {
  if (Serial.available() >= 2) {
    handle->data_size = Serial.read() << 8;
    handle->data_size |= Serial.read();
    if(handle->data_size == 0){
      Serial.println("OK: Premaure end of data");
      Serial.flush();
      return;
    }
    int len = Serial.readBytes(handle->data_buffer, handle->data_size);

    if (len != handle->data_size) {
      char msg[50];
      sprintf(msg, "Not enough data, expected %d, got %i", handle->data_size, len);
      logError(msg);
      return;
    }
    if (handle->address + len > handle->mem_size) {
      logError("Address out of range");
      return;
    }

    // Serial.print("INFO: Write to address 0x");
    // Serial.print(handle->address, 16);
    // Serial.print(", buffer size 0x");
    // Serial.println(handle->data_size, 16);
    // Serial.flush();

    setProgramerMode();
    handle->firestarter_write_data(handle);
    setComunicationMode();

    if (handle->response_code == RESPONSE_CODE_ERROR) {
      logError(handle->response_msg);
      return;
    }
    Serial.print("OK: Data written, address 0x");
    Serial.print(handle->address, 16);

    Serial.print(" - 0x");
    handle->address += handle->data_size;
    Serial.println(handle->address, 16);

    resetTimeout();
    if (handle->address >= handle->mem_size) {
      Serial.println("OK: Memory written");
      Serial.flush();
      handle->state = STATE_DONE;
      return;
    }

  }
}

void readVoltage(firestarter_handle_t* handle) {
  if (handle->init) {
    handle->init = 0;
    uint8_t ctrl = read_from_register(CONTROL_REGISTER);
    if (handle->state == STATE_READ_VPP) {
      write_to_register(CONTROL_REGISTER, ctrl | REGULATOR | VPE_TO_VPP | VPE_ENABLE);
    }
    else if (handle->state == STATE_READ_VCC) {
      write_to_register(CONTROL_REGISTER, ctrl & ~REGULATOR);
    }

    resetTimeout();
  }
  if (!waitCheckForOK()) {
    return;
  }


  float voltage = rurp_read_voltage();

  Serial.print("DATA: ");
  switch (handle->state) {
  case STATE_READ_VCC:
    Serial.print("VCC");
    break;
  case STATE_READ_VPP:
    Serial.print("VPP");
    break;
  }
  Serial.print(" voltage: ");
  Serial.print(voltage);
  Serial.println("v");
  Serial.flush();
  delay(200);
  resetTimeout();
}

void setupProm(firestarter_handle_t* handle) {
  if (Serial.available() <= 0) {
    return;
  }
  int len = Serial.readBytes(handle->data_buffer, DATA_BUFFER_SIZE);
  if (len == 0) {
    logError("Empty input");
    return;
  }

  jsmn_parser parser;
  jsmn_init(&parser);
  int token_count = jsmn_parse(&parser, handle->data_buffer, len, tokens, NUMBER_JSNM_TOKENS);

  if (token_count < 0) {
    logError((const char*)handle->data_buffer);
    return;
  }

  handle->state = json_get_state(handle->data_buffer, tokens, token_count);
  handle->init = 1;

  if (handle->state < STATE_READ_VPP) {
    json_parse(handle->data_buffer, tokens, token_count, handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
      logError(handle->response_msg);
      return;
    }
    int res = configure_memory(handle);
    if (!res) {
      logError("Could not configure chip");
      return;
    }
    Serial.print("INFO: EPROM memory size 0x");
    Serial.println(handle->mem_size, 16);
      Serial.flush();

  }
  else if (handle->state == STATE_CONFIG) {
    rurp_configuration_t* config = rurp_get_config();
    int res = json_parse_config(handle->data_buffer, tokens, token_count, config);
    if (res < 0) {
      logError(handle->data_buffer);
      return;
    }
    else if (res == 1) {
      rurp_save_config();
    }
  }
  Serial.print("OK: state 0x");
  Serial.println(handle->state, 16);
  Serial.flush();
  resetTimeout();
}

void getVersion() {
  Serial.print("OK: ");
  Serial.println(VERSION);
  Serial.flush();
  handle.state = STATE_DONE;
}

void getConfig() {
  rurp_configuration_t* rurp_config = rurp_get_config();
  Serial.print("OK: VCC: ");
  Serial.print(rurp_config->vcc);
  Serial.print("v, R1 (R16): ");
  Serial.print(rurp_config->r1);
  Serial.print(" ohms, R2 (R14+R15): ");
  Serial.print(rurp_config->r2);
  Serial.println(" ohms");
  Serial.flush();
  handle.state = STATE_DONE;
}

void loop() {
  if (handle.state != STATE_IDLE && timeout < millis()) {
    setProgramerMode();
    delay(100);
    setComunicationMode();
    logError("Timeout");
    resetTimeout();
    handle.state = STATE_DONE;
  }

  switch (handle.state) {
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
    setProgramerMode();
    set_control_pin(CHIP_ENABLE, 1);
    set_control_pin(OUTPUT_ENABLE, 1);
    write_to_register(CONTROL_REGISTER, 0x00);
    write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    setComunicationMode();
    handle.state = STATE_IDLE;
    break;
  case STATE_READ_VPP:
  case STATE_READ_VCC:
    readVoltage(&handle);
    break;
  case STATE_ERROR:
    handle.state = STATE_DONE;
    break;
  case STATE_IDLE:
    setupProm(&handle);
    break;
  case STATE_VERSION:
    getVersion();
    break;
  case STATE_CONFIG:
    getConfig();
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
  set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 1);
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
