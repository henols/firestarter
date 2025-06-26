#include "hardware_operations.h"
#include "firestarter.h"
#include "logging.h"
#include "rurp_shield.h"
#include "version.h"
#include "operation_utils.h"
#include <Arduino.h>
#include <stdlib.h>


void hw_version_overide(char* revStr);
void hw_init_read_voltage(firestarter_handle_t* handle);

bool hw_read_voltage(firestarter_handle_t* handle) {
  if (!op_check_for_ok(handle)) {
    return false;
  }

  if (handle->operation_state) {
    debug("Read voltage");
    int res = op_execute_init(hw_init_read_voltage, handle);
    if (res <= 0) {
      return true;
    }
  }

  double voltage = rurp_read_voltage();
  const char* type = (handle->cmd == CMD_READ_VPE) ? "VPE" : "VPP";
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
  // rurp_get_hardware_revision();
  debug("Get FW version");
  log_ok_const(FW_VERSION);
  return true;
}


#ifdef HARDWARE_REVISION
bool hw_get_version(firestarter_handle_t* handle) {
  debug("Get HW version");
  char revStr[24];
  hw_version_overide(revStr);
  log_ok_format("Rev%d%s", rurp_get_physical_hardware_revision(), revStr);
  return true;
}
#endif

bool hw_get_config(firestarter_handle_t* handle) {
  debug("Get config");
  rurp_configuration_t* rurp_config = rurp_get_config();
#ifdef HARDWARE_REVISION
  char revStr[24];
  hw_version_overide(revStr);
  log_ok_format("R1: %ld, R2: %ld%s", rurp_config->r1, rurp_config->r2, revStr);
#else
  log_ok_format("R1: %ld, R2: %ld", rurp_config->r1, rurp_config->r2);
#endif
  return true;
}


void hw_init_read_voltage(firestarter_handle_t* handle) {
  debug("Init read voltage");
  #ifdef HARDWARE_REVISION
  if (rurp_get_hardware_revision() == REVISION_0) {
    firestarter_error_response("Rev0 dont support reading VPP/VPE");
    return;
  }
#endif
  if (handle->cmd == CMD_READ_VPP) {
    debug("Setting up VPP");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP); // Enable regulator and drop voltage to VPP
    copy_to_buffer(handle->response_msg, "Setting up VPP");
  }
  else if (handle->cmd == CMD_READ_VPE) {
    debug("Setting up VPE");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR); // Enable regulator
  }
  else {
    firestarter_error_response("Error cmd");
  }
}

#ifdef HARDWARE_REVISION
void hw_version_overide(char* revStr) {
  rurp_configuration_t* rurp_config = rurp_get_config();
  if (rurp_config->hardware_revision < 0xFF) {
    sprintf(revStr, ", Override HW: Rev%d", rurp_config->hardware_revision);
  }
  else {
    revStr[0] = '\0';
  }
}
#endif
