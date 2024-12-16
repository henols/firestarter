/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "firestarter.h"
#include <Arduino.h>
#include <stdlib.h>

#include "ic_operations.h"
#include "hw_operations.h"

#include "json_parser.h"
#include "logging.h"
#include "utils.h"
#include "rurp_shield.h"
#include "memory.h"
#include "version.h"

#include "debug.h"

#define RX 0
#define TX 1



bool init_programmer(firestarter_handle_t* handle);
bool parse_json(firestarter_handle_t* handle);
bool state_done(firestarter_handle_t* handle);

firestarter_handle_t handle;

unsigned long timeout = 0;

void setup() {
  rurp_setup();
  handle.state = STATE_IDLE;
  debug("Firestarter started");
  debug_format("Firmware version: %s", VERSION);
  debug_format("Hardware revision: %s", rurp_get_physical_hardware_revision());
}

bool parse_json(firestarter_handle_t* handle) {
  debug("Parse JSON");
  log_info_msg((const char*)handle->data_buffer);

  jsmn_parser parser;
  jsmntok_t tokens[NUMBER_JSNM_TOKENS];

  jsmn_init(&parser);
  int token_count = jsmn_parse(&parser, handle->data_buffer, handle->data_size, tokens, NUMBER_JSNM_TOKENS);
  log_info_format(handle->response_msg, "Token count: %d", token_count);
  handle->response_msg[0] = '\0';
  if (token_count <= 0) {
    log_error_msg((const char*)handle->data_buffer);
    return false;
  }

  handle->state = json_get_state(handle->data_buffer, tokens, token_count);
  handle->init = 1;

  if (handle->state < STATE_READ_VPP) {
    json_parse(handle->data_buffer, tokens, token_count, handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
      log_error_msg(handle->response_msg);
      return false;
    }
    if (!execute_function(configure_memory, handle)) {
      log_error("Could not configure chip");
      return false;
    }
  }
  else if (handle->state == STATE_CONFIG) {
    rurp_configuration_t* config = rurp_get_config();
    int res = json_parse_config(handle->data_buffer, tokens, token_count, config);
    if (res < 0) {
      log_error("Could not parse config");
      return false;
    }
    else if (res == 1) {
      rurp_save_config();
    }
  }
  return true;
}

bool init_programmer(firestarter_handle_t* handle) {

  if (rurp_communication_available() <= 0) {
    return false;
  }

  handle->response_code = RESPONSE_CODE_OK;
  handle->data_size = rurp_communication_read_bytes(handle->data_buffer, DATA_BUFFER_SIZE);
  if (handle->data_size == 0) {
    log_error("Empty input");
    return true;
  }
  debug("Setup");
  handle->data_buffer[handle->data_size] = '\0';
  log_info_format(handle->response_msg, "Setup buffer size: %d", handle->data_size);

  if(!parse_json(handle)){
    log_error("Could not parse JSON");
    return true;
  };

  if (handle->state == 0) {
    log_error_format(handle->response_msg, "Unknown state: %s", handle->data_buffer);
    return true;
  }

  if (handle->state > STATE_IDLE && handle->state < STATE_READ_VPP) {
    log_info_format(handle->response_msg, "EPROM memory size 0x%lx", handle->mem_size);
  }

#ifdef HARDWARE_REVISION
  log_ok_format(handle->response_msg, "FW: %s:%s, HW: Rev%d, State 0x%02x", VERSION, BOARD_NAME, rurp_get_hardware_revision(), handle->state);
#else
  log_ok_format(handle->response_msg, "FW: %s, State 0x%02x", VERSION, handle->state);
#endif
  return false;
}

bool state_done(firestarter_handle_t* handle) {
  debug("State done");
  rurp_set_programmer_mode();
  rurp_set_control_pin(CHIP_ENABLE, 1);
  rurp_set_control_pin(OUTPUT_ENABLE, 1);
  rurp_write_to_register(CONTROL_REGISTER, 0x00);
  rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
  rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
  handle->state = STATE_IDLE;
  handle->response_code = RESPONSE_CODE_OK;
  rurp_set_communication_mode();
  handle->response_msg[0] = '\0';
  return false;
}

void loop() {
  if (handle.state != STATE_IDLE && timeout < millis()) {
    log_error_buf(handle.response_msg, "Timeout");
    reset_timeout();
    handle.state = STATE_DONE;
  }

  bool done = false;
  switch (handle.state) {
  case STATE_READ:
    done = read(&handle);
    break;
  case STATE_WRITE:
    done = write(&handle);
    break;
  case STATE_ERASE:
    done = erase(&handle);
    break;
  case STATE_BLANK_CHECK:
    done = blank_check(&handle);
    break;
  case STATE_CHECK_CHIP_ID:
    done = check_chip_id(&handle);
    break;
  case STATE_DONE:
    done = state_done(&handle);
    break;
  case STATE_READ_VPP:
  case STATE_READ_VPE:
    done = read_voltage(&handle);
    break;
  case STATE_IDLE:
    done = init_programmer(&handle);
    break;
  case STATE_FW_VERSION:
    done = get_fw_version(&handle);
    break;
#ifdef HARDWARE_REVISION
  case STATE_HW_VERSION:
    done = get_hw_version(&handle);
    break;
#endif
  case STATE_CONFIG:
    done = get_config(&handle);
    break;

  default:
    log_error_format(handle.response_msg, "Unknown state: %d", handle.state);
    done = true;
    break;
  }
  if (done) {
    handle.state = STATE_DONE;
  }
  else {
    reset_timeout();
  }
}

void reset_timeout() {
  timeout = millis() + 1000;
}





