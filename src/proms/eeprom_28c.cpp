/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eeprom_28c.h"

#include <Arduino.h>

#include "firestarter.h"
#include "flash_utils.h"
#include "logging.h"
#include "memory_utils.h"
#include "operation_utils.h"

#define PAGE_SIZE 64

void eeprom28c_write_init(firestarter_handle_t* handle);
void eeprom28c_write_execute(firestarter_handle_t* handle);
static bool eeprom28c_wait_for_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected);

// AT28C SDP disable: 6-write sequence to magic addresses
const byte_flip_t EEPROM_SDP_DISABLE[] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x20},
};

void configure_eeprom28c(firestarter_handle_t* handle) {
    debug("Configuring EEPROM 28C");
    // AT28C page write timing requires fast consecutive writes; no pulse delay needed
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}

// A9-12V chip-identification check for AT28C EEPROM family (SAF-05).
// Mirrors eprom_get_chip_id (eprom.cpp:186-197) for the read mechanism and
// flash_intel_check_chip_id (flash_intel.cpp:146-155) for compare + response.
// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,
// AT28C64 = 0x1FC0/0x1FC1, etc. Caller-visible via response_code only;
// no declaration in eeprom_28c.h (static — internal linkage only).
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    debug("Check chip ID (28C)");
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    uint32_t mfr_addr = handle->mem_size - 64;  // 0x7FC0 (AT28C256) / 0x1FC0 (AT28C64) / ...
    uint16_t chip_id = handle->firestarter_get_data(handle, mfr_addr) << 8;
    chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    if (chip_id != handle->chip_id) {
        int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);
    }
}

void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip identity via A9-12V (SAF-05) BEFORE SDP-disable (D-08: fail-fast
    // on identity leaves the chip write-protected on mismatch).
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // Disable SDP (Software Data Protection) before writing.
    // The 6-write sequence must complete within the inter-byte timing window.
    // flash_util_byte_flipping uses fu_flash_flip_data which has no pulse_delay.
    flash_execute_command(EEPROM_SDP_DISABLE);
    // Wait for SDP disable internal write cycle to complete
    if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
        return;
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void eeprom28c_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!eeprom28c_wait_for_write(handle, address, data)) {
                return;
            }
        }
    }
}

static bool eeprom28c_wait_for_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 2000; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) {
            return true;
        }
    }
    firestarter_error_response_format("EEPROM timeout at 0x%06lx: wrote 0x%02x got 0x%02x", address, expected, observed);
    return false;
}
