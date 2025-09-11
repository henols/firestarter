/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"

#include <Arduino.h>

#include "firestarter.h"
#include "logging.h"
#include "memory_utils.h"
#include "rurp_shield.h"
#include "operation_utils.h"


#define NUMBER_OF_RETRIES 20

void eprom_erase_execute(firestarter_handle_t* handle);

void eprom_write_init(firestarter_handle_t* handle);
void eprom_write_execute(firestarter_handle_t* handle);
void eprom_check_chip_id_init(firestarter_handle_t* handle);
void eprom_check_chip_id_execute(firestarter_handle_t* handle);

void eprom_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool cmd);
uint16_t eprom_get_chip_id(firestarter_handle_t* handle);

void eprom_check_vpp(firestarter_handle_t* handle);

void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code);
void eprom_internal_erase(firestarter_handle_t* handle);

void (*ep_set_control_register)(struct firestarter_handle*, rurp_register_t, bool);

void eprom_generic_init(firestarter_handle_t* handle);

void configure_eprom(firestarter_handle_t* handle) {
    debug("Configuring EPROM");

    handle->firestarter_operation_init = eprom_generic_init;

    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eprom_write_init;
            handle->firestarter_operation_main = eprom_write_execute;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = eprom_erase_execute;
            if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
                handle->firestarter_operation_end = mem_util_blank_check;
            }
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_CHECK_CHIP_ID:
            handle->firestarter_operation_init = eprom_check_chip_id_init;
            handle->firestarter_operation_main = eprom_check_chip_id_execute;
            break;
    }

    ep_set_control_register = handle->firestarter_set_control_register;
    handle->firestarter_set_control_register = eprom_set_control_register;
}

void eprom_check_chip_id_init(firestarter_handle_t* handle) {
    eprom_check_vpp(handle);
}

void eprom_check_chip_id_execute(firestarter_handle_t* handle) {
    debug("Check chip ID");
    eprom_internal_check_chip_id(handle, RESPONSE_CODE_ERROR);
}

void eprom_erase_execute(firestarter_handle_t* handle) {
    debug("Erase");
    eprom_internal_erase(handle);
}

void eprom_write_init(firestarter_handle_t* handle) {
    if(!is_operation_in_progress(handle)){
        eprom_generic_init(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
        
        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                eprom_internal_erase(handle);
            } else {
                copy_to_buffer(handle->response_msg, "Skipping erase.");
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

// New helper to program only the bytes that have failed so far
static void program_mismatched_bytes(firestarter_handle_t* handle, const uint8_t* mismatch_bitmask) {
    eprom_set_control_register(handle, VPE_ENABLE, 1);
    delay(10); // Consider making this a named constant
    for (uint32_t i = 0; i < handle->data_size; i++) {
        // Use the corrected bitwise-AND operator here
        if (mismatch_bitmask[i / 8] & (1 << (i % 8))) {
            handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
        }
    }
    eprom_set_control_register(handle, VPE_ENABLE, 0);
}

// New helper to verify bytes and update the mismatch mask
static int verify_and_update_mask(firestarter_handle_t* handle, uint8_t* mismatch_bitmask) {
    int mismatch_count = 0;
    for (uint32_t i = 0; i < handle->data_size; i++) {
        if (handle->firestarter_get_data(handle, (handle->address + i)) != (uint8_t)handle->data_buffer[i]) {
            mismatch_count++;
            mismatch_bitmask[i / 8] |= (1 << (i % 8)); // Set bit for mismatch
        } else {
            mismatch_bitmask[i / 8] &= ~(1 << (i % 8)); // Clear bit for match
        }
    }
    
    return mismatch_count;
}

void eprom_write_execute(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
        if (is_flag_set(FLAG_VPE_AS_VPP)) {
            handle->firestarter_set_control_register(handle, REGULATOR, 1);
        } else {
            handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
        }
        delay(500);
    }

    uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8];
    // Use memset for cleaner initialization
    memset(mismatch_bitmask, 0xFF, sizeof(mismatch_bitmask));

    int mismatch = 0;
    int retries = 0;
    uint32_t org_delay = handle->pulse_delay;

    for (int w = 0; w < NUMBER_OF_RETRIES; w++) {
        program_mismatched_bytes(handle, mismatch_bitmask);
        
        mismatch = verify_and_update_mask(handle, mismatch_bitmask);

        if (!mismatch) {
            handle->response_msg[0] = '\0';
            if (retries > 0) {
                format(handle->response_msg, "Number of retries: %d", retries);
            }
            handle->pulse_delay = org_delay;
            return;
        }

        retries = w + 1;
        handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);
        debug_format("Mismatch, retrying with increased pulse delay from %d to %d", org_delay, handle->pulse_delay);
    }

    handle->firestarter_set_control_register(handle, REGULATOR, 0);
    firestarter_error_response_format("Failed to write memory, 0x%06x, retries: %d, bad bytes: %d", handle->address, retries, mismatch);
}

// Use this function to set the control register and flip VPE_ENABLE bit to VPE_ENABLE or P1_VPP_ENABLE
void eprom_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & VPE_ENABLE && using_p1_as_vpp(handle)) {
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
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
    return chip_id;
}

void eprom_check_vpp(firestarter_handle_t* handle) {
    debug("Check VPP");
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
    if (is_flag_set(FLAG_VPE_AS_VPP)) {
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
    } else {
        // Regulator defaults to VEP (~2V higher than VPP so it must be dropped)
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    }

    delay(100);
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
    handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 0);
}

void eprom_internal_erase(firestarter_handle_t* handle) {
    debug("Internal erase");
    rurp_chip_input();
    handle->firestarter_set_control_register(handle, REGULATOR, 1);  // Enable regulator without dropping resistor
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_ENABLE, 1);  // Erase with VPE - assumes VPE_TO_VPP isn't set and left active previously
    delay(100);
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);
    // After the erase pulse, we should disable the chip to end the programming cycle.
    rurp_chip_disable();

    handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE | VPE_ENABLE, 0);
}

void eprom_generic_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eprom_check_vpp(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
        eprom_internal_check_chip_id(handle, is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
    }
}

void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code) {
    debug("Check chip ID");
    uint16_t chip_id = eprom_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        firestarter_response_format(error_code, "Chip ID: %#x dont match: %#x", chip_id, handle->chip_id);
    }
}
