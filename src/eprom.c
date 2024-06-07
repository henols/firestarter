/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"
#include <stdio.h>
#include "config.h"
#include "firestarter.h"
#include "rurp_shield.h"

void eprom_erase(firestarter_handle_t* handle);
void eprom_write_data(firestarter_handle_t* handle);
uint16_t eprom_get_chip_id(firestarter_handle_t* handle);

int configure_eprom(firestarter_handle_t* handle) {
    handle->firestarter_write_data = eprom_write_data;
    return 1;
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
    delay(500);
    set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    set_control_pin(CHIP_ENABLE, 1);

    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE | VPE_ENABLE, 0);
}

void eprom_write_data(firestarter_handle_t* handle) {
    if (handle->init) {
        handle->init = 0;
        if (handle->has_chip_id) {
            uint16_t chip_id = eprom_get_chip_id(handle);
            if (chip_id != handle->chip_id) {
                handle->response_code = RESPONSE_CODE_ERROR;
                sprintf(handle->response_msg, "Chip ID %u does not match %u", chip_id, handle->chip_id);
                return;
            }
        }
        if (handle->can_erase) {
            eprom_erase(handle);
#ifdef EPROM_BLANK_CHECK
            set_control_pin(CHIP_ENABLE, 0);
            for (uint32_t i = 0; i < handle->mem_size; i++) {
                if (handle->firestarter_get_data(handle, i) != 0xFF) {
                    handle->response_code = RESPONSE_CODE_ERROR;
                    sprintf(handle->response_msg, "Failed to erase memory, at 0x%x", i);

                    return;
                }
            }
            set_control_pin(CHIP_ENABLE, 1);
#endif
        }
    }

    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
        delay(100);
    }
    handle->firestarter_set_control_register(handle, VPE_TO_VPP, 1);
    delay(10);
    handle->firestarter_set_control_register(handle, VPE_ENABLE, 1);

    for (uint32_t i = 0; i < DATA_BUFFER_SIZE; i++) {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }

    handle->firestarter_set_control_register(handle, VPE_TO_VPP | VPE_ENABLE, 0);


#ifdef EPROM_WRITE_CHECK
    for (uint32_t i = 0; i < DATA_BUFFER_SIZE; i++) {
        uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
        if (byte != handle->data_buffer[i]) {
            handle->response_code = RESPONSE_CODE_ERROR;
            sprintf(handle->response_msg, "Got: %#x, exp: %#x, at %#x", byte, handle->data_buffer[i] , handle->address + i);
            return;
        }
    }
#endif

    // uint8_t mismatch_bitmask[32];  // Array to store mismatch bits (32 bytes * 8 bits = 256 bits)
    // uint8_t mismatch = 0;
    // for (int i = 0; i < 32; i++) {
    //     mismatch_bitmask[i] = 0xFF;
    // }
    // for (int w = 0; w < 10; w++) {
    //     mismatch = 0;
    //     handle->firestarter_set_control_register(handle, VPE_TO_VPP | REGULATOR, 1);
    //     delay(50);
    //     handle->firestarter_set_control_register(handle, VPE_ENABLE, 1);
    //     // Iterate through the mismatch bitmask to find all mismatched positions
    //     for (int byte_index = 0; byte_index < 32; byte_index++) {
    //         for (int bit_index = 0; bit_index < 8; bit_index++) {
    //             if (mismatch_bitmask[byte_index] & (1 << bit_index)) {
    //                 // Calculate the original position in the data buffer
    //                 int pos = (byte_index * 8) + bit_index;
    //                 handle->firestarter_set_data(handle, handle->address + pos, handle->data_buffer[pos]);
    //             }
    //         }
    //     }
    //     handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP | VPE_ENABLE, 0);

    //     for (int i = 0; i < 32; i++) {
    //         mismatch_bitmask[i] = 0;
    //     }

    //     for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
    //         if (handle->firestarter_get_data(handle, handle->address + i) != handle->data_buffer[i]) {
    //             mismatch++;
    //             mismatch_bitmask[i / 8] |= (1 << (i % 8));
    //         }
    //     }
    //     if (!mismatch) {
    //         handle->response_code = RESPONSE_CODE_OK;
    //         return;
    //     }
    // }
    // sprintf(handle->response_msg, "Failed to write memory, at 0x%x, nr %d", handle->address, mismatch);
    // handle->response_code = RESPONSE_CODE_ERROR;
    handle->response_code = RESPONSE_CODE_OK;

}

