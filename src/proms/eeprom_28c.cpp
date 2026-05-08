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

void eeprom28c_write_init(firestarter_handle_t* handle) {
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
