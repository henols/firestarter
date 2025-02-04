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
  int res = op_execute_init(handle->firestarter_operation_init, handle);
  if (res <= 0) {
    return true;
  }

  res = op_execute_function(handle->firestarter_operation_execute, handle);
  if (res <= 0) {
    return true;
  }

  log_data_format("Read data from address 0x%lx to 0x%lx", handle->address, handle->address + handle->data_size);
  rurp_communication_write(handle->data_buffer, handle->data_size);
  // debug_format("Read buffer: %.10s...", handle->data_buffer);


  handle->address += handle->data_size;
  if (handle->address > handle->mem_size - 1) {
    while (!op_check_for_ok(handle));
    if (op_execute_function(handle->firestarter_operation_end, handle) > 0) {
      log_ok_const("Memmory read");
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
      if (op_execute_function(handle->firestarter_operation_end, handle) > 0) {
        log_ok_const("Memory written");
      }
      return true;
    }

    log_ok_format("Reciving %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format("Not enough data, expected %d, got %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error_const("Address out of range");
      return true;
    }

    int res = op_execute_init(handle->firestarter_operation_init, handle);
    if (res <= 0) {
      return true;
    }

    // debug("Write PROM exec");
    res = op_execute_function(handle->firestarter_operation_execute, handle);
    if (res <= 0) {
      return true;
    }

    log_ok_format("Data written to address %lx - %lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      if (op_execute_function(handle->firestarter_operation_end, handle) > 0) {
        log_ok_const("Memory written");
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
      if (op_execute_function(handle->firestarter_operation_end, handle) > 0) {
        log_ok_const("Memory verified");
      }
      return true;
    }

    log_ok_format("Reciving %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format("Not enough data, expected %d, got %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error_const("Address out of range");
      return true;
    }

    int res = op_execute_init(handle->firestarter_operation_init, handle);
    if (res <= 0) {
      return true;
    }

    res = op_execute_function(handle->firestarter_operation_execute, handle);
    if (res <= 0) {
      return true;
    }

    log_ok_format("Data verified address %lx - %lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      if (op_execute_function(handle->firestarter_operation_end, handle) > 0) {
        log_ok_const("Memory verified");
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
  if (is_flag_set(FLAG_CAN_ERASE) and excecute_operation(handle)) {
    if (handle->response_code == RESPONSE_CODE_OK) {
      log_ok_const("Chip is erased");
    }
    else {
      log_error_const("Chip erase failed");
    }
  }
  else {
    log_error_const("Erase not supported");
  }
  return true;
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }
  debug("Check Chip ID");
  if (handle->chip_id == 0) {
    log_error_const("Chip ID not present");
    return true;
  }
  if (excecute_operation(handle)) {
    if (handle->response_code == RESPONSE_CODE_OK) {
      log_ok_const("Chip ID matches");
    }
  }
  else {
    log_error_const("Check Chip ID is not supported");
  }
  return true;
}

bool eprom_blank_check(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }
  debug("Blank check PROM");
  if (excecute_operation(handle)) {
    if (handle->response_code == RESPONSE_CODE_OK) {
      log_ok_const("Chip is blank");
    }
  }
  else {
    log_error_const("Blank check is not supported");
  }
  return true;
}


bool excecute_operation(firestarter_handle_t* handle) {
  if (handle->firestarter_operation_execute) {
    int res = op_execute_init(handle->firestarter_operation_init, handle);
    if (res <= 0) {
      return true;
    }
    res = op_execute_function(handle->firestarter_operation_execute, handle);
    if (res <= 0) {
      return true;
    }
    op_execute_function(handle->firestarter_operation_end, handle);
    return true;
  }
  return false;
}
