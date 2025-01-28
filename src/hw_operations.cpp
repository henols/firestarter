#include "hw_operations.h"
#include "firestarter.h"
#include "logging.h"
#include "operation_utils.h"
#include "rurp_shield.h"
#include "version.h"
#include <Arduino.h>
#include <stdlib.h>


void create_overide_text(char* revStr);
void init_read_voltage(firestarter_handle_t* handle);

bool read_voltage(firestarter_handle_t* handle) {
  if (!op_wait_for_ok(handle)) {
    return false;
  }

  if(handle->init) {
    debug("Read voltage");
    int res = op_execute_init(init_read_voltage, handle);
    if (res <= 0) {
    //  log_info_const("Fail voltage");
      return true;
    }
    log_ok_const("Voltage setup");
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

bool get_fw_version(firestarter_handle_t* handle) {
  debug("Get FW version");
  log_ok_const(FW_VERSION);
  return true;
}


#ifdef HARDWARE_REVISION
bool get_hw_version(firestarter_handle_t* handle) {
  debug("Get HW version");
  char revStr[24];
  create_overide_text(revStr);
  log_ok_format("Rev%d%s", rurp_get_physical_hardware_revision(), revStr);
  return true;
}
#endif

bool get_config(firestarter_handle_t* handle) {
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
    if (rurp_get_hardware_revision() == REVISION_0) {
      copy_to_buffer(handle->response_msg,"Rev0 dont support reading VPP/VPE");
      handle->response_code = RESPONSE_CODE_ERROR;
      return;
    }

  if (handle->state == STATE_READ_VPP) {
    debug("Setting up VPP");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP); // Enable regulator and drop voltage to VPP
    copy_to_buffer(handle->response_msg, "Setting up VPP");
    return;
  }
  else if (handle->state == STATE_READ_VPE) {
    debug("Setting up VPE");
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR); // Enable regulator
    copy_to_buffer(handle->response_msg, "Setting up VPE");
    return;
  }
  copy_to_buffer(handle->response_msg, "Error state");
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
