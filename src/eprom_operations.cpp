/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom_operations.h"
#include "firestarter.h"
#include "logging.h"
#include "operation_utils.h"
#include "rurp_shield.h"

bool excecute_operation(firestarter_handle_t* handle);

bool eprom_read(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }

  debug("Read PROM");
  if (!op_execute_init(handle->firestarter_operation_init, handle)) {
    return true;
  }
  
  if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
    return true;
  }

  log_data_format("Read: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);
  rurp_communication_write(handle->data_buffer, handle->data_size);
  // debug_format("Read buffer: %.10s...", handle->data_buffer);

  handle->address += handle->data_size;
  if (handle->address > handle->mem_size - 1) {
    while (!op_check_for_ok(handle));
    if (op_execute_end(handle->firestarter_operation_end, handle)) {
      log_ok_const("Read done");
    }
    return true;
  }
  return false;
}

bool eprom_write(firestarter_handle_t* handle) {

  if (rurp_communication_available() >= 2) {
    debug("Write PROM");
    handle->data_size = rurp_communication_read() << 8;
    handle->data_size |= rurp_communication_read();
    if (handle->data_size == 0) {
      log_warn_const("Premature end of data");
      if (op_execute_end(handle->firestarter_operation_end, handle)) {
        log_ok_const("Write done");
      }
      return true;
    }

    log_ok_format("Expecting %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format("Not enough data: %d > %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error_const("Address out of range");
      return true;
    }

    if (!op_execute_init(handle->firestarter_operation_init, handle)) {
      return true;
    }

    // debug("Write PROM exec");
    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
      return true;
    }

    log_ok_format("Write: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      if (op_execute_end(handle->firestarter_operation_end, handle)) {
        log_ok_const("Write done");
      }
      return true;
    }
  }
  return false;
}

bool eprom_verify(firestarter_handle_t* handle) {

  if (rurp_communication_available() >= 2) {
    debug("Verify PROM");
    handle->data_size = rurp_communication_read() << 8;
    handle->data_size |= rurp_communication_read();
    if (handle->data_size == 0) {
      log_warn_const("Premature end of data");
      if (op_execute_end(handle->firestarter_operation_end, handle) > 0) {
        log_ok_const("Verify done");
      }
      return true;
    }

    log_ok_format("Expecting %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format("Not enough data: %d > %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error_const("Address out of range");
      return true;
    }

    if (!op_execute_init(handle->firestarter_operation_init, handle)) {
      return true;
    }

    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
      return true;
    }

    log_ok_format("Verify: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      if (op_execute_end(handle->firestarter_operation_end, handle)) {
        log_ok_const("Verify done");
      }
      return true;
    }
  }
  return false;
}

bool eprom_erase(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }

  debug("Erase PROM");
  if (is_flag_set(FLAG_CAN_ERASE) && excecute_operation(handle)) {
    if (handle->response_code == RESPONSE_CODE_OK) {
      log_ok_const("Erased");
    }
    else {
      log_error_const("Failed");
    }
  }
  else {
    log_error_const("Not supported");
  }
  return true;
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }
  debug("Check Chip ID");
  if (handle->chip_id == 0) {
    log_error_const("No chip ID");
    return true;
  }
  if (excecute_operation(handle)) {
    if (handle->response_code == RESPONSE_CODE_OK) {
      log_ok_const("Chip ID matches");
    }
  }
  else {
    log_error_const("Not supported");
  }
  return true;
}

bool eprom_blank_check(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }

  debug("Blank check");
  if (!op_execute_init(handle->firestarter_operation_init, handle)) {
    return true;
  }
  
  if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
    return true;
  }

  log_data_format("Blank check: 0x%04lx - 0x%04lx", handle->address, handle->address + handle->data_size);
  rurp_communication_write(handle->data_buffer, handle->data_size);
  // debug_format("Read buffer: %.10s...", handle->data_buffer);

  handle->address += handle->data_size;
  if (handle->address > handle->mem_size - 1) {
    while (!op_check_for_ok(handle));
    if (op_execute_end(handle->firestarter_operation_end, handle)) {
      log_ok_const("Blank check done");
    }
    return true;
  }
  return false;

  // debug("Blank check PROM");
  // if (excecute_operation(handle)) {
  //   if (handle->response_code == RESPONSE_CODE_OK) {
  //     log_ok_const("Blank");
  //   }
  // }
  // else {
  //   log_error_const("Not supported");
  // }
  // return true;
}


bool excecute_operation(firestarter_handle_t* handle) {
  if (handle->firestarter_operation_execute) {
    if (!op_execute_init(handle->firestarter_operation_init, handle)) {
      return true;
    }
    if (!op_execute_function(handle->firestarter_operation_execute, handle)) {
      return true;
    }
    op_execute_end(handle->firestarter_operation_end, handle);
    return true;
  }
  return false;
}
