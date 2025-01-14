#include "ic_operations.h"
#include "firestarter.h"
#include "logging.h"
#include "utils.h"
#include "rurp_shield.h"

bool read(firestarter_handle_t* handle) {
  if (!wait_for_ok(handle)) {
    return false;
  }

  debug("Read PROM");
  int res = execute_init(handle->firestarter_read_init, handle);
  if (res <= 0) {
    return true;
  }

  res = execute_function(handle->firestarter_read_data, handle);
  if (res <= 0) {
    return true;
  }

  log_data_format(handle->response_msg, "Read data from address 0x%lx to 0x%lx", handle->address, handle->address + handle->data_size);
  rurp_communication_write(handle->data_buffer, handle->data_size);
  // debug_format("Read buffer: %.10s...", handle->data_buffer);


  handle->address += handle->data_size;
  if (handle->address > handle->mem_size - 1) {
    while (!wait_for_ok(handle));
    log_ok("Memmory read");
    return true;
  }
  return false;
}

bool write(firestarter_handle_t* handle) {

  if (rurp_communication_available() >= 2) {
    debug("Write PROM");
    handle->data_size = rurp_communication_read() << 8;
    handle->data_size |= rurp_communication_read();
    if (handle->data_size == 0) {
      log_warn("Premature end of data");
      log_ok("Memory written");
      return true;
    }

    log_ok_format(handle->response_msg, "Reciving %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format(handle->response_msg, "Not enough data, expected %d, got %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error("Address out of range");
      return true;
    }

    int res = execute_init(handle->firestarter_write_init, handle);
    if (res <= 0) {
      return true;
    }

    // debug("Write PROM exec");
    res = execute_function(handle->firestarter_write_data, handle);
    if (res <= 0) {
      return true;
    }

    log_ok_format(handle->response_msg, "Data written to address %lx - %lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      log_ok("Memory written");
      return true;
    }
  }
  return false;
}

bool verify(firestarter_handle_t* handle) {

  if (rurp_communication_available() >= 2) {
    debug("Verify PROM");
    handle->data_size = rurp_communication_read() << 8;
    handle->data_size |= rurp_communication_read();
    if (handle->data_size == 0) {
      log_warn("Premature end of data");
      log_ok("Memory verified");
      return true;
    }

    log_ok_format(handle->response_msg, "Reciving %d bytes", handle->data_size);
    int len = rurp_communication_read_bytes(handle->data_buffer, handle->data_size);

    if ((uint32_t)len != handle->data_size) {
      log_error_format(handle->response_msg, "Not enough data, expected %d, got %d", (int)handle->data_size, len);
      return true;
    }

    if (handle->address + len > handle->mem_size) {
      log_error("Address out of range");
      return true;
    }

    int res = execute_init(handle->firestarter_verify_init, handle);
    if (res <= 0) {
      return true;
    }

    res = execute_function(handle->firestarter_verify, handle);
    if (res <= 0) {
      return true;
    }

    log_ok_format(handle->response_msg, "Data verified address %lx - %lx", handle->address, handle->address + handle->data_size);

    handle->address += handle->data_size;
    if (handle->address >= handle->mem_size) {
      log_ok("Memory verified");
      return true;
    }
  }
  return false;
}

bool erase(firestarter_handle_t* handle) {
  if (handle->firestarter_erase) {
    debug("Erase PROM");
    int res = execute_init(handle->firestarter_erase_init, handle);
    if (res <= 0) {
      return true;
    }

    res = execute_function(handle->firestarter_erase, handle);
    if (res <= 0) {
      return true;
    }
    log_ok("Chip is erased");
  }
  else {
    log_error("Erase not supported");
  }
  return true;
}

bool check_chip_id(firestarter_handle_t* handle) {
  debug("Check Chip ID");
  if (handle->firestarter_check_chip_id) {
    int res = execute_init(handle->firestarter_check_chip_id_init, handle);
    if (res <= 0) {
      return true;
    }

    res = execute_function(handle->firestarter_check_chip_id, handle);
    if (res <= 0) {
      return true;
    }
    log_ok("Chip ID matches");
  }
  else {
    log_error("Check Chip ID is not supported");
  }
  return true;
}

bool blank_check(firestarter_handle_t* handle) {
  debug("Blank check PROM");
  if (handle->firestarter_blank_check) {
    int res = execute_init(handle->firestarter_blank_check_init, handle);
    if (res <= 0) {
      return true;
    }

    res = execute_function(handle->firestarter_blank_check, handle);
    if (res <= 0) {
      return true;
    }
    log_ok("Chip is blank");
  }
  else {
    log_error("Blank check is not supported");
  }
  return true;
}

