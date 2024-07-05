/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"
#include <Arduino.h>
#include <stdio.h>
#include "config.h"
#include "firestarter.h"
#include "rurp_shield.h"

void eprom_erase(firestarter_handle_t* handle);
void eprom_write_init(firestarter_handle_t* handle);
void eprom_write_data(firestarter_handle_t* handle);
uint16_t eprom_get_chip_id(firestarter_handle_t* handle);
void eprom_set_control_register(firestarter_handle_t* handle, uint8_t bit, bool state);

void (*set_control_register)(struct firestarter_handle*, uint8_t, bool);

void configure_eprom(firestarter_handle_t* handle) {
    handle->firestarter_write_init = eprom_write_init;
    handle->firestarter_write_data = eprom_write_data;
    set_control_register = handle->firestarter_set_control_register;
    handle->firestarter_set_control_register = eprom_set_control_register;
    handle->response_code = RESPONSE_CODE_OK;
}

uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(50);

    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_TO_VPP, 1);
    delay(100);
    set_control_pin(CHIP_ENABLE, 0);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    set_control_pin(CHIP_ENABLE, 1);
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE | VPE_TO_VPP, 0);
    return chip_id;
}

void eprom_erase(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_ENABLE, 1);
    delay(100);
    set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    set_control_pin(CHIP_ENABLE, 1);

    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE | VPE_ENABLE, 0);
}

void eprom_write_init(firestarter_handle_t* handle) {
    if (handle->has_chip_id) {
        uint16_t chip_id = eprom_get_chip_id(handle);
        if (chip_id != handle->chip_id) {
            handle->response_code = RESPONSE_CODE_ERROR;
            sprintf(handle->response_msg, "Chip ID %#x dont match expected ID %#x", chip_id, handle->chip_id);
            return;
        }
    }
    if (handle->can_erase && !handle->skip_erase) {
        eprom_erase(handle);
    }
#ifdef EPROM_BLANK_CHECK
    if (handle->blank_check) {
        for (uint32_t i = 0; i < handle->mem_size; i++) {
            if (handle->firestarter_get_data(handle, i) != 0xFF) {
                handle->response_code = RESPONSE_CODE_ERROR;
                sprintf(handle->response_msg, "Memory is not blank, at %#lx", i);
                return;
            }
        }
    }
#endif
}

void eprom_write_data(firestarter_handle_t* handle) {
    if (handle->init) {
        handle->init = 0;
    }

    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
        delay(100);
    }
    uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8];  // Array to store mismatch bits (32 bytes * 8 bits = 256 bits)
    int mismatch = 0;
    int rewrites = 0;
    for (int i = 0; i < DATA_BUFFER_SIZE / 8; i++) {
        mismatch_bitmask[i] = 0xFF;
    }
    for (int w = 0; w < 20; w++) {
        mismatch = 0;
        handle->firestarter_set_control_register(handle, VPE_TO_VPP | VPE_ENABLE, 1);
        // Iterate through the mismatch bitmask to find all mismatched positions
        for (uint32_t i = 0; i < handle->data_size; i++) {
            if (mismatch_bitmask[i / 8] |= (1 << (i % 8))) {
                handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
                if (w > 0) {
                    rewrites++;
                }
            }
        }
        handle->firestarter_set_control_register(handle, VPE_TO_VPP | VPE_ENABLE, 0);
        for (uint32_t i = 0; i < handle->data_size; i++) {
            if (handle->firestarter_get_data(handle, (handle->address + i)) != (uint8_t)handle->data_buffer[i]) {
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
            handle->response_code = RESPONSE_CODE_OK;
            handle->response_msg[0] = '\0';
            if (handle->verbose && rewrites > 0) {
                sprintf(handle->response_msg, "Number of rewrites %d", rewrites);
            }
            return;
        }
    }
    handle->firestarter_set_control_register(handle, REGULATOR, 0);
    sprintf(handle->response_msg, "Failed to write memory, at 0x%lx, nr %d", handle->address, mismatch);
    handle->response_code = RESPONSE_CODE_ERROR;
}

// Use this function to set the control register and flip VPE_ENABLE bit to VPE_ENABLE or P1_VPP_ENABLE
void eprom_set_control_register(firestarter_handle_t* handle, uint8_t bit, bool state) {
    if(bit & VPE_ENABLE && handle->bus_config.vpp_line == 1) {
        bit &= ~VPE_ENABLE;
        bit |= P1_VPP_ENABLE;
    }
    set_control_register(handle, bit, state);
}
