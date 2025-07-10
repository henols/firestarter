#include "hardware_operations.h"

#include <Arduino.h>
#include <stdlib.h>

#include "firestarter.h"
#include "logging.h"
#include "operation_utils.h"
#include "rurp_shield.h"
#include "version.h"

void hw_version_override(char* revStr);

bool hw_read_voltage(firestarter_handle_t* handle) {
    // State 0: Initialization. This runs only once per command.
    if (handle->operation_state == 0) {
        debug("Init read voltage");
#ifdef HARDWARE_REVISION
        if (rurp_get_hardware_revision() == REVISION_0) {
            log_error_const("Rev0 dont support reading VPP/VPE");
            return true;  // Finish command with an error.
        }
#endif
        rurp_set_programmer_mode();
        if (handle->cmd == CMD_READ_VPP) {
            debug("Setting up VPP");
            rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP);
        } else if (handle->cmd == CMD_READ_VPE) {
            debug("Setting up VPE");
            rurp_write_to_register(CONTROL_REGISTER, REGULATOR);
        } else {
            rurp_set_communication_mode();
            log_error_const("Error cmd");
            return true;  // Finish command with an error.
        }
        delay(100);                  // Allow voltage to stabilize.
        rurp_set_communication_mode(); // Switch back to communication mode to send the ready signal.
        handle->operation_state = 1; // Transition to the reading state.

        // Send a ready signal to the client to prompt it for the first ACK.
        // This establishes a handshake and avoids a race condition.
        send_ack_const("Ready");

        // Return false to keep the command active, but do not fall through.
        // The next call will be in state 1, ready to receive the client's ACK.
        return false;
    }

    // State 1+: Continuous reading loop.
    // We expect an "OK" (ACK) from the client to trigger a reading.
    if (op_get_message(handle) != OP_MSG_ACK) {
        // If we haven't received an ACK, we just wait.
        // Returning false keeps the command active without doing anything.
        return false;
    }

    rurp_set_programmer_mode();
    // An ACK was received. Proceed with taking a measurement.
    uint16_t vcc_mv = rurp_read_vcc_mv();
    uint16_t voltage_mv = rurp_read_voltage_mv(vcc_mv);
    rurp_set_communication_mode();

    const char* type = (handle->cmd == CMD_READ_VPE) ? "VPE" : "VPP";

    // Send the data back to the client.
    log_data_format("%s: %u.%02uV, Internal VCC: %u.%02uV", type, voltage_mv / 1000, (voltage_mv % 1000) / 10,
                    vcc_mv / 1000, (vcc_mv % 1000) / 10);
                    
    op_reset_timeout();  // Reset the command timeout since we're actively communicating.

    // Return false to indicate the command is not finished. It will continue
    // to wait for the next ACK from the client.
    return false;
}

bool fw_get_version(firestarter_handle_t* handle) {
    debug("Get FW version");
    send_ack_const(FW_VERSION);
    return true;
}

#ifdef HARDWARE_REVISION
bool hw_get_version(firestarter_handle_t* handle) {
    debug("Get HW version");
    char revStr[24] = {0};
    hw_version_override(revStr);
    send_ack_format("Rev%d%s", rurp_get_physical_hardware_revision(), revStr);
    return true;
}
#endif

bool hw_get_config(firestarter_handle_t* handle) {
    debug("Get config");
    rurp_configuration_t* rurp_config = rurp_get_config();
#ifdef HARDWARE_REVISION
    char revStr[24] = {0};
    hw_version_override(revStr);
    send_ack_format("R1: %ld, R2: %ld%s", rurp_config->r1, rurp_config->r2, revStr);
#else
    send_ack_format("R1: %ld, R2: %ld", rurp_config->r1, rurp_config->r2);
#endif
    return true;
}

#ifdef HARDWARE_REVISION
void hw_version_override(char* revStr) {
    rurp_configuration_t* rurp_config = rurp_get_config();
    if (rurp_config->hardware_revision < 0xFF) {
        strcpy_P(revStr, PSTR(", Override HW: Rev"));
        itoa(rurp_config->hardware_revision, revStr + strlen(revStr), 10);
    } else {
        revStr[0] = '\0';
    }
}
#endif