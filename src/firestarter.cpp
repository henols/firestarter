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

#include "operation_utils.h"
#include "rurp_shield.h"
#include "memory.h"
#include "version.h"
#ifdef DEV_TOOLS
#include "dev_tools.h"
#endif

#define RX 0
#define TX 1

bool init_programmer(firestarter_handle_t* handle);
bool parse_json(firestarter_handle_t* handle);
void command_done(firestarter_handle_t* handle);

firestarter_handle_t handle;

unsigned long timeout = 0;

void setup() {
#ifdef SERIAL_DEBUG
  debug_msg_buffer = (char*)malloc(80);
  debug_setup();
#endif

  rurp_load_config();
  rurp_detect_hardware_revision();
  rurp_board_setup();

  handle.state = STATE_IDLE;
  debug("Firestarter started");
  debug_format("Firmware version: %s", VERSION);
  debug_format("Hardware revision: %d", rurp_get_physical_hardware_revision());
}

bool parse_json(firestarter_handle_t* handle) {
  debug("Parse JSON");
  log_info((const char*)handle->data_buffer);

  jsmn_parser parser;
  jsmntok_t tokens[NUMBER_JSNM_TOKENS];

  jsmn_init(&parser);
  int token_count = jsmn_parse(&parser, handle->data_buffer, handle->data_size, tokens, NUMBER_JSNM_TOKENS);
  handle->response_msg[0] = '\0';
  if (token_count <= 0) {
    log_error_const("Bad JSON");
    return false;
  }
  log_info_format("Token count: %d", token_count);

  handle->state = json_get_state(handle->data_buffer, tokens, token_count);
  if ( handle->state < 0)  {
    log_error_const("Unknown state");
    return false;
  }
  
  debug_format("State: %d", handle->state);
  if (handle->state < STATE_READ_VPP) {
    json_parse(handle->data_buffer, tokens, token_count, handle);
    log_info_format("Force: %d", is_flag_set(FLAG_FORCE));
    log_info_format("Can erase: %d", is_flag_set(FLAG_CAN_ERASE));
    log_info_format("Skip erase: %d", is_flag_set(FLAG_SKIP_ERASE));
    log_info_format("Skip blank check: %d", is_flag_set(FLAG_SKIP_BLANK_CHECK));
    log_info_format("VPE as VPP: %d", is_flag_set(FLAG_VPE_AS_VPP));
    log_info_format("Output enable: %d", is_flag_set(FLAG_OUTPUT_ENABLE));
    log_info_format("Chip enable: %d", is_flag_set(FLAG_CHIP_ENABLE));
    if (handle->response_code == RESPONSE_CODE_ERROR) {
      log_error(handle->response_msg);
      return false;
    }
    if (!op_execute_function(configure_memory, handle)) {
      log_error_const("Could not configure chip");
      return false;
    }
  }
  else if (handle->state == STATE_CONFIG) {
    rurp_configuration_t* config = rurp_get_config();
    int res = json_parse_config(handle->data_buffer, tokens, token_count, config);
    if (res < 0) {
      log_error_const("Could not parse config");
      return false;
    }
    else if (res == 1) {
      rurp_save_config(config);
    }
  }
  return true;
}

bool init_programmer(firestarter_handle_t* handle) {
  handle->response_code = RESPONSE_CODE_OK;
  handle->init = 1;

  handle->data_size = rurp_communication_read_bytes(handle->data_buffer, DATA_BUFFER_SIZE);
  log_info_format("Setup buffer size: %d", handle->data_size);
  if (handle->data_size == 0) {
    log_error_const("Empty input");
    return true;
  }
  debug("Setup");
  handle->data_buffer[handle->data_size] = '\0';

  if (!parse_json(handle)) {
    return true;
  };

  if (handle->state > STATE_IDLE && handle->state < STATE_READ_VPP) {
    log_info_format("EPROM memory size 0x%lx", handle->mem_size);
  }

#ifdef HARDWARE_REVISION
#define PARSE_RESPONSE "FW: " FW_VERSION ", HW: Rev%d, State 0x%02x"
  log_ok_format(PARSE_RESPONSE, rurp_get_hardware_revision(), handle->state);
#else
#define PARSE_RESPONSE "FW: " FW_VERSION ", State 0x%02x"
  log_ok_format(PARSE_RESPONSE, handle->state);
#endif
  return false;
}

void command_done(firestarter_handle_t* handle) {
  debug("State done");
  rurp_set_programmer_mode();
  rurp_chip_disable();
  // rurp_set_control_pin(OUTPUT_ENABLE, 1);
  rurp_write_to_register(CONTROL_REGISTER, 0x00);
  rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
  rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
  handle->state = STATE_IDLE;
  rurp_set_communication_mode();
  handle->response_msg[0] = '\0';
}

void loop() {
  if (handle.state != STATE_IDLE && timeout < millis()) {
    log_error_const_buf(handle.response_msg, "Timeout");
    command_done(&handle);
  }
  else
    if (handle.state == STATE_IDLE) {
      if (rurp_communication_available() > 0) {
        if (init_programmer(&handle)) {
          return;
        }
      }
      else {
        return;
      }
    }

  bool done = false;
  switch (handle.state) {
  case STATE_READ:
    done = read(&handle);
    break;
  case STATE_WRITE:
    done = write(&handle);
    break;
  case STATE_VERIFY:
    done = verify(&handle);
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
  case STATE_READ_VPP:
  case STATE_READ_VPE:
    done = read_voltage(&handle);
    break;
  case STATE_IDLE:
    break;
  case STATE_FW_VERSION:
    done = get_fw_version(&handle);
    break;
#ifdef HARDWARE_REVISION
  case STATE_HW_VERSION:
    done = get_hw_version(&handle);
    break;
#endif
#ifdef DEV_TOOLS
  case  STATE_DEV_REGISTER:
    done = dt_set_registers(&handle);
    break;
  case STATE_DEV_ADDRESS:
    done = dt_set_address(&handle);
    break;
#endif

  case STATE_CONFIG:
    done = get_config(&handle);
    break;

  default:
    log_error_format_buf(handle.response_msg, "Unknown state: %d", handle.state);
    done = true;
    break;
  }
  if (done) {
    command_done(&handle);
  }

}

void op_reset_timeout() {
  timeout = millis() + 1000;
}





