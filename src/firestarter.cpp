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
#include "logging.h"
#include "rurp_shield.h"
#include "memory.h"
#include "version.h"

 // 1892 bytes of SRAM

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
void setCommunicationMode();
void resetTimeout();

int executeFunction(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle);
int checkResponse(firestarter_handle_t* handle);


void setup() {
  rurp_setup();
  setCommunicationMode();
  handle.state = STATE_IDLE;
}

void resetTimeout()
{
  timeout = millis() + 1000;
}

int waitCheckForOK() {
  if (Serial.available() < 2) {
    return 0;
  }
  if (Serial.read() != 'O' || Serial.read() != 'K') {
    logInfoBuf(handle.response_msg, "Expecting OK");
    resetTimeout();
    return 0;
  }
  return 1;
}

void readProm(firestarter_handle_t* handle) {
  if (!waitCheckForOK()) {
    return;
  }

  int res = executeFunction(handle->firestarter_read_data, handle);
  if (res <= 0) {
    return;
  }

  logDataf(handle->response_msg, "Read data from address 0x%lx to 0x%lx", handle->address, handle->address + DATA_BUFFER_SIZE);

  Serial.write(handle->data_buffer, DATA_BUFFER_SIZE);
  Serial.flush();
  handle->address += DATA_BUFFER_SIZE;
  if (handle->address == handle->mem_size) {
    logOkf(handle->response_msg, "Read data from address 0x00 to 0x%lx", handle->mem_size);
    handle->state = STATE_DONE;
    return;
  }
  resetTimeout();
}


void eraseProm(firestarter_handle_t* handle) {
  if (handle->firestarter_erase) {
    int res = executeFunction(handle->firestarter_erase, handle);
    if (res <= 0) {
      return;
    }
    logOkBuf(handle->response_msg, "Chip is erased");
    handle->state = STATE_DONE;
  }
  else {
    logError("Erase not supported");
  }
}

void blankCheck(firestarter_handle_t* handle) {
  if (handle->firestarter_blank_check) {
    int res = executeFunction(handle->firestarter_blank_check, handle);
    if (res <= 0) {
      return;
    }
    logOkBuf(handle->response_msg, "Chip is blank");
    handle->state = STATE_DONE;
  }
  else {
    logError("Blank check not supported");
  }
}




void writeProm(firestarter_handle_t* handle) {
  if (Serial.available() >= 2) {
    handle->data_size = Serial.read() << 8;
    handle->data_size |= Serial.read();
    if (handle->data_size == 0) {
      logOk("Premature end of data");
      return;
    }
    int len = Serial.readBytes(handle->data_buffer, handle->data_size);

    if (handle->init && handle->firestarter_write_init != NULL) {
      handle->init = 0;
      int res = executeFunction(handle->firestarter_write_init, handle);
      if (res <= 0) {
        return;
      }
    }


    if ((uint32_t)len != handle->data_size) {
      logErrorf(handle->response_msg, "Not enough data, expected %d, got %d", (int)handle->data_size, len);
      return;
    }
    if (handle->address + len > handle->mem_size) {
      logError("Address out of range");
      return;
    }

    int res = executeFunction(handle->firestarter_write_data, handle);
    if (res <= 0) {
      return;
    }
    logOkf(handle->response_msg, "Data written to address %lX - %lX", handle->address, handle->address + handle->data_size);
    handle->address += handle->data_size;
    resetTimeout();
    if (handle->address >= handle->mem_size) {
      logOk("Memory written");
      handle->state = STATE_DONE;
      return;
    }

  }
}

void readVoltage(firestarter_handle_t* handle) {
  if (handle->init) {
    handle->init = 0;
    // uint8_t ctrl = read_from_register(CONTROL_REGISTER);
    if (handle->state == STATE_READ_VPP) {
      rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP ); //Only enable regulator and drop voltage to VPP
    }
    else if (handle->state == STATE_READ_VCC) {
      rurp_write_to_register(CONTROL_REGISTER, 0);
    }

    resetTimeout();
  }
  if (!waitCheckForOK()) {
    return;
  }

  double voltage = rurp_read_voltage();
  const char* type = (handle->state == STATE_READ_VCC) ? "VCC" : "VPP";
  char vStr[10];
  dtostrf(voltage, 2, 2, vStr);

  logDataf(handle->response_msg, "%s Voltage: %sv", type, vStr);
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
  jsmntok_t tokens[NUMBER_JSNM_TOKENS];

  jsmn_init(&parser);
  int token_count = jsmn_parse(&parser, handle->data_buffer, len, tokens, NUMBER_JSNM_TOKENS);

  if (token_count < 0) {
    logErrorMsg((const char*)handle->data_buffer);
    return;
  }

  handle->state = json_get_state(handle->data_buffer, tokens, token_count);
  handle->init = 1;

  if (handle->state < STATE_READ_VPP) {
    json_parse(handle->data_buffer, tokens, token_count, handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
      logErrorMsg(handle->response_msg);
      return;
    }

    configure_memory(handle);
    int res = checkResponse(handle);
    if (res <= 0) {
      logError("Could not configure chip");
      return;
    }

    logInfof(handle->response_msg, "EPROM memory size 0x%lx", handle->mem_size);

  }
  else if (handle->state == STATE_CONFIG) {
    rurp_configuration_t* config = rurp_get_config();
    int res = json_parse_config(handle->data_buffer, tokens, token_count, config);
    if (res < 0) {
      logErrorMsg(handle->data_buffer);
      return;
    }
    else if (res == 1) {
      rurp_save_config();
    }
  }
  logOkf(handle->response_msg, "Setup done, state 0x%x", handle->state);
  resetTimeout();
}

void getVersion() {
  logOkBuf(handle.response_msg, VERSION);
  handle.state = STATE_DONE;
}

void getConfig(firestarter_handle_t* handle) {
  rurp_configuration_t* rurp_config = rurp_get_config();
  char vccStr[10];
  dtostrf(rurp_config->vcc, 4, 2, vccStr);
  logOkf(handle->response_msg, "VCC: %s, R1: %ld, R2: %ld", vccStr, rurp_config->r1, rurp_config->r2);
  handle->state = STATE_DONE;
}

void loop() {
  handle.response_msg[0] = '\0';
  if (handle.state != STATE_IDLE && timeout < millis()) {
    setProgramerMode();
    delay(100);
    setCommunicationMode();
    logErrorBuf(handle.response_msg, "Timeout");
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
  case STATE_BLANK_CHECK:
    blankCheck(&handle);
    break;
  case STATE_DONE:
    setProgramerMode();
    rurp_set_control_pin(CHIP_ENABLE, 1);
    rurp_set_control_pin(OUTPUT_ENABLE, 1);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    setCommunicationMode();
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
    getConfig(&handle);
    break;

  default:
    logErrorf(handle.response_msg, "Unknown state: %d", handle.state);
    break;
  }
}


int checkResponse(firestarter_handle_t* handle) {
  if (handle->response_code == RESPONSE_CODE_OK) {
    logInfoMsg(handle->response_msg);
    return 1;
  }
  else if (handle->response_code == RESPONSE_CODE_WARNING) {
    logWarnMsg(handle->response_msg);
    return 1;
  }
  else if (handle->response_code == RESPONSE_CODE_ERROR) {
    logErrorMsg(handle->response_msg);
    return 0;
  }
  return 0;
}

int executeFunction(void (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
  setProgramerMode();
  callback(handle);
  setCommunicationMode();
  delayMicroseconds(50);
  return checkResponse(handle);
}



void setCommunicationMode() {
  rurp_set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 1);
  DDRD &= ~(0x01);
  Serial.begin(MONITOR_SPEED); // Initialize serial port

  while (!Serial)
  {
    delayMicroseconds(1);
  }
  Serial.flush();
  delay(1);
}

void setProgramerMode() {
  Serial.end(); // Close serial port
  DDRD |= 0x01;
}

void log(const char* type, const char* msg) {
  Serial.print(type);
  Serial.print(": ");
  Serial.println(msg);
  Serial.flush();
}

