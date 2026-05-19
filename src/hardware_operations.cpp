#include "hardware_operations.h"

#include <Arduino.h>
#include <stdlib.h>

#include "firestarter.h"
#include "logging.h"
#include "logging_id.h"
#include "messages.h"
#include "operation_utils.h"
#include "rurp_shield.h"
#include "version.h"

bool hw_read_voltage(firestarter_handle_t* handle) {
    // State 0: Initialization. This runs only once per command.
    if (handle->operation_state == 0) {
        LOG_DEBUG_ID_SUB(DBG_INIT_READ_VOLTAGE);
#ifdef HARDWARE_REVISION
        if (rurp_get_hardware_revision() == REVISION_0) {
            LOG_ERROR_ID(MSG_ERR_REV0_VPP_RD);
            return true;  // Finish command with an error.
        }
#endif
        rurp_set_programmer_mode();
        if (handle->cmd == CMD_READ_VPP) {
            LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPP);
            rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP);
        } else if (handle->cmd == CMD_READ_VPE) {
            LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPE);
            rurp_write_to_register(CONTROL_REGISTER, REGULATOR);
        } else {
            rurp_set_communication_mode();
            LOG_ERROR_ID(MSG_ERR_CMD);
            return true;  // Finish command with an error.
        }
        delay(100);                     // Allow voltage to stabilize.
        rurp_set_communication_mode();  // Switch back to communication mode to send the ready signal.
        handle->operation_state = 1;    // Transition to the reading state.

        // Send a ready signal to the client to prompt it for the first ACK.
        // This establishes a handshake and avoids a race condition.
        LOG_OK_ID(MSG_OK_READY);

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
    delay(500);

    // An ACK was received. Proceed with taking a measurement.
    uint16_t vcc_mv = rurp_read_vcc_mv();
    uint16_t voltage_mv = rurp_read_voltage_mv();

    // Compute pre-rounded integer/decimal tenths for each voltage (catalog expects 4 x u16).
    uint16_t v_int  = (uint16_t)((voltage_mv + 50) / 1000);
    uint16_t v_dec  = (uint16_t)(((voltage_mv + 50) / 100) % 10);
    uint16_t vc_int = (uint16_t)((vcc_mv + 50) / 1000);
    uint16_t vc_dec = (uint16_t)(((vcc_mv + 50) / 100) % 10);

    // Send the data back to the client as a structured ID frame.
    if (handle->cmd == CMD_READ_VPE) {
        LOG_DATA_ID_U16x4(MSG_DATA_VPE_VOLTAGE, v_int, v_dec, vc_int, vc_dec);
    } else {
        LOG_DATA_ID_U16x4(MSG_DATA_VPP_VOLTAGE, v_int, v_dec, vc_int, vc_dec);
    }

    op_reset_timeout();  // Reset the command timeout since we're actively communicating.

    // Return false to indicate the command is not finished. It will continue
    // to wait for the next ACK from the client.
    return false;
}

bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // Phase 9 / LFW-05: lone surviving text-format emit. Inlined here after the
    // legacy send-ack-const / rurp-log-P chain was deleted. F("OK: FW: ") keeps
    // the literal in PROGMEM with no named symbol — same exemption class as
    // MAGIC_PREAMBLE / CRC8_TABLE (SC#1).
    SERIAL_PORT.print(F("OK: FW: "));
    SERIAL_PORT.println(FW_VERSION);
    SERIAL_PORT.flush();
    return true;
}

#ifdef HARDWARE_REVISION
bool hw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_HW_VERSION);
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint8_t physical  = (uint8_t)rurp_get_physical_hardware_revision();
    uint8_t effective = (rurp_config->hardware_revision < 0xFF)
                        ? (uint8_t)rurp_config->hardware_revision
                        : 0xFF;  // P-02 sentinel: no override active
    LOG_OK_ID_U8_U8(MSG_OK_REV, physical, effective);
    return true;
}
#endif

bool hw_get_config(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_CONFIG);
    rurp_configuration_t* rurp_config = rurp_get_config();
    // P-03: pack u32 r1 + u32 r2 + u8 override (0xFF = no override) into 9 bytes.
    uint8_t override_byte = (rurp_config->hardware_revision < 0xFF)
                            ? (uint8_t)rurp_config->hardware_revision
                            : 0xFF;
    uint8_t _cfg[9];
    _cfg[0] = (uint8_t)((rurp_config->r1 >> 24) & 0xFF);
    _cfg[1] = (uint8_t)((rurp_config->r1 >> 16) & 0xFF);
    _cfg[2] = (uint8_t)((rurp_config->r1 >>  8) & 0xFF);
    _cfg[3] = (uint8_t)((rurp_config->r1      ) & 0xFF);
    _cfg[4] = (uint8_t)((rurp_config->r2 >> 24) & 0xFF);
    _cfg[5] = (uint8_t)((rurp_config->r2 >> 16) & 0xFF);
    _cfg[6] = (uint8_t)((rurp_config->r2 >>  8) & 0xFF);
    _cfg[7] = (uint8_t)((rurp_config->r2      ) & 0xFF);
    _cfg[8] = override_byte;
    LOG_ID_BYTES(MSG_OK_CFG, _cfg, 9);
    return true;
}

