/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"
#include <avr/pgmspace.h>
#include <stdio.h>
#include "config.h"
#include "firestarter.h"
#include "rurp_shield.h"
#include <Arduino.h>
#include "logging.h"
#include "debug.h"


void eprom_erase(firestarter_handle_t* handle);
void eprom_blank_check(firestarter_handle_t* handle);
void eprom_write_init(firestarter_handle_t* handle);
void eprom_write_data(firestarter_handle_t* handle);
uint16_t eprom_get_chip_id(firestarter_handle_t* handle);
void eprom_set_control_register(firestarter_handle_t* handle, register_t bit, bool state);

void (*set_control_register)(struct firestarter_handle*, register_t, bool);

void configure_eprom(firestarter_handle_t* handle) {
    handle->firestarter_write_init = eprom_write_init;
    handle->firestarter_write_data = eprom_write_data;
    set_control_register = handle->firestarter_set_control_register;
    handle->firestarter_set_control_register = eprom_set_control_register;
    handle->firestarter_erase = eprom_erase;
    handle->firestarter_blank_check = eprom_blank_check;
}

uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);

    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
    delay(100);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    rurp_set_control_pin(CHIP_ENABLE, 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    return chip_id;
}

void eprom_check_chip_id(firestarter_handle_t* handle) {
    uint16_t chip_id = eprom_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        handle->response_code = handle->force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        format(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_id, handle->chip_id);
    }
}

void eprom_internal_erase(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR, 1); //Enable regulator without dropping resistor
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_ENABLE, 1); //Erase with VPE - assumes VPE_TO_VPP isn't set and left active previously
    delay(100);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    rurp_set_control_pin(CHIP_ENABLE, 1);

    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE | VPE_ENABLE, 0);
}

#ifdef TEST_VPP_BEFORE_WRITE
void eprom_check_vpp(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    delay(100);
    double vpp = rurp_read_voltage();
#ifdef DEBUG
    char vppStr[6];
    dtostrf(vpp, 2, 2, vppStr);
    debug_format("Checking VPP voltage %s", vppStr);
#endif

    if (vpp > handle->vpp * 1.02) {
        handle->response_code = handle->force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        char vStr[6];
        dtostrf(vpp, 2, 2, vStr);
        char rStr[6];
        dtostrf(handle->vpp, 2, 2, rStr);
        format(handle->response_msg, "VPP voltage is too high: %sv expected: %sv", vStr, rStr);
    }
    else if (vpp < handle->vpp * .95) {
        handle->response_code = RESPONSE_CODE_WARNING;
        char vStr[6];
        dtostrf(vpp, 2, 2, vStr);
        char rStr[6];
        dtostrf(handle->vpp, 2, 2, rStr);
        format(handle->response_msg, "VPP voltage is low: %sv expected: %sv", vStr, rStr);
    }
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 0);
}
#endif

void eprom_erase(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eprom_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    if (handle->can_erase) {
        eprom_internal_erase(handle);
    }
    else {
        copyToBuffer(handle->response_msg, "Erase not supported");
        handle->response_code = RESPONSE_CODE_ERROR;
    }
}

void eprom_blank_check(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->mem_size; i++) {
        uint8_t val = handle->firestarter_get_data(handle, i);
        if (val != 0xFF) {
            handle->response_code = RESPONSE_CODE_ERROR;
            format(handle->response_msg, "Memory is not blank, at 0x%06x, value: 0x%02x", i, val);
            return;
        }
    }
}


void eprom_write_init(firestarter_handle_t* handle) {
#ifdef TEST_VPP_BEFORE_WRITE
    // Breaks everything for some reason
    eprom_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
#endif
    if (handle->chip_id > 0) {
        eprom_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }

    if (handle->can_erase && !handle->skip_erase) {
        eprom_internal_erase(handle);
    }
    else {
        copyToBuffer(handle->response_msg, "Skipping erase of memory");
    }
#ifdef EPROM_BLANK_CHECK
    if (handle->blank_check) {
        eprom_blank_check(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
#endif
}

void eprom_write_data(firestarter_handle_t* handle) {

    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1); // Regulator defaults to VEP (~2V higher than VPP so it must be dropped)
        delay(500);
    }
    uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8];  // Array to store mismatch bits (32 bytes * 8 bits = 256 bits)
    int mismatch = 0;
    int rewrites = 0;
    for (int i = 0; i < DATA_BUFFER_SIZE / 8; i++) {
        mismatch_bitmask[i] = 0xFF;
    }
    for (int w = 0; w < 20; w++) {
        mismatch = 0;
        handle->firestarter_set_control_register(handle, VPE_ENABLE, 1);
        // Iterate through the mismatch bitmask to find all mismatched positions
        for (uint32_t i = 0; i < handle->data_size; i++) {
            if (mismatch_bitmask[i / 8] |= (1 << (i % 8))) {
                handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
                if (w > 0) {
                    rewrites++;
                }
            }
        }
        handle->firestarter_set_control_register(handle, VPE_ENABLE, 0);
        for (uint32_t i = 0; i < handle->data_size; i++) {
            if (handle->firestarter_get_data(handle, (handle->address + i)) != (uint8_t)handle->data_buffer[i]) {
                // debug_format("Mismatch at 0x%lx, expected %c, got %c", handle->address + i, handle->data_buffer[i], handle->firestarter_get_data(handle, handle->address + i));
                mismatch++;
                if (mismatch == 1) {
                }
                mismatch_bitmask[i / 8] |= (1 << (i % 8));
            }
            else {
                mismatch_bitmask[i / 8] &= ~(1 << (i % 8));
            }
        }

        if (!mismatch) {
            handle->response_msg[0] = '\0';
            if (rewrites > 0) {
                format(handle->response_msg, "Number of rewrites %d", rewrites);
            }
            return;
        }
        debug("Mismatch, retrying");
    }
    handle->firestarter_set_control_register(handle, REGULATOR, 0);
    format(handle->response_msg, "Failed to write memory, at 0x%06x, nr %d", handle->address, mismatch);
    handle->response_code = RESPONSE_CODE_ERROR;
}

// Use this function to set the control register and flip VPE_ENABLE bit to VPE_ENABLE or P1_VPP_ENABLE
void eprom_set_control_register(firestarter_handle_t* handle, register_t bit, bool state) {
    if (bit & VPE_ENABLE && (handle->bus_config.vpp_line == 15 || handle->bus_config.vpp_line == 21)) {
        bit &= ~VPE_ENABLE;
        bit |= P1_VPP_ENABLE;
    }
    set_control_register(handle, bit, state);
}
