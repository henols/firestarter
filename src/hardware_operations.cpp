#include "hardware_operations.h"
#include "firestarter.h"
#include "logging.h"
#include "rurp_shield.h"
#include "version.h"
#include "operation_utils.h"
#include <Arduino.h>
#include <stdlib.h>


void create_overide_text(char* revStr);
void init_read_voltage(firestarter_handle_t* handle);

bool hw_read_voltage(firestarter_handle_t* handle) {
  if (handle->init) {
    debug("Read voltage");
    if (rurp_get_hardware_revision() == REVISION_0) {
      log_error_const("Rev0 dont support reading VPP/VPE");
      return true;
    }
    handle->init = 0;
    int res = op_execute_function(init_read_voltage, handle);
    if (res <= 0) {
      return true;
    }
    log_ok_const("Voltage read setup");
  }

  if (!op_wait_for_ok(handle)) {
    return false;
  }

  double voltage = rurp_read_voltage();
  const char* type = (handle->state == STATE_READ_VPE) ? "VPE" : "VPP";
  char vStr[10];
  dtostrf(voltage, 2, 2, vStr);
  char vcc[10];
  dtostrf(rurp_read_vcc(), 2, 2, vcc);
  log_data_format("%s: %sv, Internal VCC: %sv", type, vStr, vcc);
  delay(200);
  op_reset_timeout();
  return false;
}

bool fw_get_version(firestarter_handle_t* handle) {
  debug("Get FW version");
  log_ok_const(FW_VERSION);
  return true;
}


#ifdef HARDWARE_REVISION
bool hw_get_version(firestarter_handle_t* handle) {
  debug("Get HW version");
  char revStr[24];
  create_overide_text(revStr);
  log_ok_format("Rev%d%s", rurp_get_physical_hardware_revision(), revStr);
  return true;
}
#endif

bool hw_get_config(firestarter_handle_t* handle) {
  debug("Get config");
  rurp_configuration_t* rurp_config = rurp_get_config();
#ifdef HARDWARE_REVISION
  char revStr[24];
  create_overide_text(revStr);
  log_ok_format("R1: %ld, R2: %ld%s", rurp_config->r1, rurp_config->r2, revStr);
#else
  log_ok_format("R1: %ld, R2: %ld", rurp_config->r1, rurp_config->r2);
#endif
  return true;
}

void init_read_voltage(firestarter_handle_t* handle) {
  debug("Init read voltage");
  if (handle->state == STATE_READ_VPP) {
    debug("Setting up VPP");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP); // Enable regulator and drop voltage to VPP
  }
  else if (handle->state == STATE_READ_VPE) {
    debug("Setting up VPP");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR); // Enable regulator
  }
}

#ifdef HARDWARE_REVISION
void create_overide_text(char* revStr) {
  rurp_configuration_t* rurp_config = rurp_get_config();
  if (rurp_config->hardware_revision < 0xFF) {
    sprintf(revStr, ", Override HW: Rev%d", rurp_config->hardware_revision);
  }
  else {
    revStr[0] = '\0';
  }
}
#endif
