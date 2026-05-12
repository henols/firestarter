/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_intel.h"

#include <Arduino.h>

#include "firestarter.h"
#include "logging.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_shield.h"

void flash_intel_write_init(firestarter_handle_t* handle);
void flash_intel_write_execute(firestarter_handle_t* handle);
void flash_intel_erase_execute(firestarter_handle_t* handle);
void flash_intel_cleanup(firestarter_handle_t* handle);
void flash_intel_check_chip_id(firestarter_handle_t* handle);
static bool flash_intel_poll_sr(firestarter_handle_t* handle, uint16_t timeout_ms);

static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP (Intel)");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    // Caller (flash_intel_write_init) already asserted REGULATOR | P1_VPP_ENABLE
    // and delayed 500ms; do not toggle the regulator here.
    uint16_t vpp_mv = rurp_read_voltage_mv();
#ifdef SERIAL_DEBUG
    debug_format("Checking VPP voltage %u mV", vpp_mv);
#endif
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV",
                                    (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                    (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV",
                                            (vpp_mv + 50) / 1000, (((vpp_mv + 50) / 100) % 10),
                                            (handle->vpp_mv + 50) / 1000, (((handle->vpp_mv + 50) / 100) % 10));
    }
    // NO regulator clear — caller continues to use REGULATOR | P1_VPP_ENABLE through the write pulse.
}

void configure_flash_intel(firestarter_handle_t* handle) {
    debug("Configuring Intel Flash");
    handle->firestarter_operation_end = flash_intel_cleanup;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = flash_intel_write_init;
            handle->firestarter_operation_main = flash_intel_write_execute;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = flash_intel_erase_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_CHECK_CHIP_ID:
            handle->firestarter_operation_init = NULL;
            handle->firestarter_operation_end = NULL;
            handle->firestarter_operation_main = flash_intel_check_chip_id;
            break;
    }
}

void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    flash_intel_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        // Safety: clear VPP regulator before early-return so 12V is not left
        // applied to socket pin 1 after an unsafe-voltage detection. Without
        // this, flash_intel_cleanup (END phase) is never reached and the
        // hazard the check exists to prevent stays asserted.
        handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
        return;
    }
    if (handle->chip_id > 0) {
        flash_intel_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
            return;
        }
    }
    if (is_flag_set(FLAG_CAN_ERASE) && !is_flag_set(FLAG_SKIP_ERASE)) {
        flash_intel_erase_execute(handle);
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void flash_intel_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, 0x40);  // program setup
        handle->firestarter_set_data(handle, address, data);  // program data
        if (!flash_intel_poll_sr(handle, 150)) {
            return;
        }
    }
}

void flash_intel_erase_execute(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    handle->firestarter_set_data(handle, 0, 0x20);  // erase setup
    handle->firestarter_set_data(handle, 0, 0xD0);  // erase confirm
    if (!flash_intel_poll_sr(handle, 15000)) {
        return;
    }
    debug("Erase complete");
}

void flash_intel_cleanup(firestarter_handle_t* handle) {
    handle->firestarter_set_data(handle, 0, 0xFF);  // reset to read array mode
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
}

static bool flash_intel_poll_sr(firestarter_handle_t* handle, uint16_t timeout_ms) {
    unsigned long deadline = millis() + timeout_ms;
    while (millis() < deadline) {
        uint8_t sr = handle->firestarter_get_data(handle, 0);
        if (sr & 0x80) {
            if (sr & 0x10) {
                firestarter_error_response("Intel flash: VPP error");
                handle->firestarter_set_data(handle, 0, 0xFF);
                return false;
            }
            if (sr & 0x08) {
                firestarter_error_response("Intel flash: program error");
                handle->firestarter_set_data(handle, 0, 0xFF);
                return false;
            }
            return true;
        }
    }
    firestarter_error_response("Intel flash: SR timeout");
    handle->firestarter_set_data(handle, 0, 0xFF);
    return false;
}

void flash_intel_check_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_data(handle, 0, 0x90);  // enter autoselect
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= handle->firestarter_get_data(handle, 0x0001);
    handle->firestarter_set_data(handle, 0, 0xFF);  // exit autoselect
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}
