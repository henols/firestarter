/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"
#include <Arduino.h>
#include <avr/pgmspace.h>
#include <stdio.h>
#include "firestarter.h"
#include "rurp_shield.h"
#include "logging.h"


void eprom_erase_execute(firestarter_handle_t* handle);
void eprom_blank_check_execute(firestarter_handle_t* handle);

void eprom_write_init(firestarter_handle_t* handle);
void eprom_write_execute(firestarter_handle_t* handle);
void eprom_check_chip_id_init(firestarter_handle_t* handle);
void eprom_check_chip_id_execute(firestarter_handle_t* handle);

void eprom_set_control_register(firestarter_handle_t* handle, register_t bit, bool state);
uint16_t eprom_get_chip_id(firestarter_handle_t* handle);

#ifdef TEST_VPP_BEFORE_OPERATION
void eprom_check_vpp(firestarter_handle_t* handle);
#endif

void eprom_internal_erase(firestarter_handle_t* handle);
void (*set_control_register)(struct firestarter_handle*, register_t, bool);

void eprom_generic_init(firestarter_handle_t* handle);

void configure_eprom(firestarter_handle_t* handle) {
    debug("Configuring EPROM");

    handle->firestarter_operation_init = eprom_generic_init;

    switch (handle->state) {
    case STATE_WRITE:
        handle->firestarter_operation_init = eprom_write_init;
        handle->firestarter_operation_execute = eprom_write_execute;
        break;
    case STATE_ERASE:
        handle->firestarter_operation_execute = eprom_erase_execute;
        handle->firestarter_operation_end = eprom_blank_check_execute;
        break;
    case STATE_BLANK_CHECK:
        handle->firestarter_operation_execute = eprom_blank_check_execute;
        break;
    case STATE_CHECK_CHIP_ID:
        handle->firestarter_operation_init = eprom_check_chip_id_init;
        handle->firestarter_operation_execute = eprom_check_chip_id_execute;
        break;
    }

    set_control_register = handle->firestarter_set_control_register;
    handle->firestarter_set_control_register = eprom_set_control_register;
}

void eprom_check_chip_id_init(firestarter_handle_t* handle) {
#ifdef TEST_VPP_BEFORE_OPERATION
    eprom_check_vpp(handle);
#endif
}

void eprom_check_chip_id_execute(firestarter_handle_t* handle) {
    debug("Check chip ID");
    uint16_t chip_id = eprom_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        handle->response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
        format(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_id, handle->chip_id);
    }
}

void eprom_erase_execute(firestarter_handle_t* handle) {
    debug("Erase");
    eprom_internal_erase(handle);
}


void eprom_blank_check_execute(firestarter_handle_t* handle) {
    debug("Blank check");
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
    eprom_generic_init(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }

    if (is_flag_set(FLAG_CAN_ERASE)) {
        if (!is_flag_set(FLAG_SKIP_ERASE)) {
            eprom_internal_erase(handle);
        }
        else {
            copy_to_buffer(handle->response_msg, "Skipping erase of memory");
        }
    }
#ifdef EPROM_BLANK_CHECK
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        eprom_blank_check_execute(handle);
    }
#endif
}

void eprom_write_execute(firestarter_handle_t* handle) {

    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        if (is_flag_set(FLAG_VPE_AS_VPP)) {
            handle->firestarter_set_control_register(handle, REGULATOR, 1);
        }
        else {
            // Regulator defaults to VEP (~2V higher than VPP so it must be dropped)
            handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
        }
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
    ep_set_control_register(handle, bit, state);
}

uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    debug("Get chip ID");
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

#ifdef TEST_VPP_BEFORE_OPERATION
void eprom_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        handle->response_code = RESPONSE_CODE_WARNING;
        strcpy(handle->response_msg, "Rev0 dont support reading VPP.");
        return;
    }
#endif
    if (is_flag_set(FLAG_VPE_AS_VPP)) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
    }
    else {
        // Regulator defaults to VEP (~2V higher than VPP so it must be dropped)
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    }

    delay(100);
    double vpp = rurp_read_voltage();
#ifdef SERIAL_DEBUG
    char vppStr[6];
    dtostrf(vpp, 2, 2, vppStr);
    debug_format("Checking VPP voltage %s", vppStr);
#endif

    if (vpp > handle->vpp * 1.02) {
        handle->response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
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

void eprom_internal_erase(firestarter_handle_t* handle) {
    debug("Internal erase");
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

void eprom_generic_init(firestarter_handle_t* handle) {
#ifdef TEST_VPP_BEFORE_OPERATION
    eprom_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
#endif
    if (handle->chip_id > 0) {
        eprom_check_chip_id_execute(handle);
    }
}
