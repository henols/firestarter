/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_type_3.h"

#include <Arduino.h>
#include "memory_utils.h"
#include "flash_utils.h"
#include "firestarter.h"
#include "logging.h"
#include "logging_id.h"
#include "operation_utils.h"

void flash3_erase_execute(firestarter_handle_t* handle);
void flash3_sector_erase(firestarter_handle_t* handle, uint32_t sector_address);
void flash3_write_init(firestarter_handle_t* handle);
void flash3_write_execute(firestarter_handle_t* handle);
void flash3_check_chip_id_execute(firestarter_handle_t* handle);

uint16_t flash3_get_chip_id(firestarter_handle_t* handle);

void flash3_generic_init(firestarter_handle_t* handle);

// Worst-case erase time for older flash chips can be up to 100ms.
// Add a 5ms buffer for safety.
const int FLASH_ERASE_DELAY_MS = 105;

void configure_flash3(firestarter_handle_t* handle) {
    debug("Configuring Flash");
    handle->firestarter_operation_init = flash3_generic_init;
    switch (handle->cmd) {
    case CMD_WRITE:
        handle->firestarter_operation_init = flash3_write_init;
        handle->firestarter_operation_main = flash3_write_execute;
        break;
    case CMD_ERASE:
        handle->firestarter_operation_main = flash3_erase_execute;
        // handle->firestarter_operation_end = memory_blank_check;
        break;
    case CMD_BLANK_CHECK:
        handle->firestarter_operation_main = mem_util_blank_check;
        break;
    case CMD_CHECK_CHIP_ID:
        handle->firestarter_operation_init = NULL;
        handle->firestarter_operation_main = flash3_check_chip_id_execute;
        break;
    }
}

void flash3_generic_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        flash3_check_chip_id_execute(handle);
    }
}


void flash3_write_init(firestarter_handle_t* handle) {
    // Gate one-time init (chip-ID + erase + erase-settle delay) behind
    // is_operation_in_progress so it runs exactly ONCE per write command.
    // Without this guard the INIT-phase state machine re-invokes
    // flash3_write_init for every 2KB chunk of the stateful blank-check
    // (mem_util_blank_check progresses 2KB per call). For a 512KB chip
    // that is 256 re-runs of: chip-ID check + chip-erase command + 105ms
    // settle delay. Each chip-erase command starts an internal erase that
    // takes ~100ms; sending another erase command before the chip
    // completes the previous one leaves it in an undefined state. The
    // accumulated 27+ seconds of pointless settle delay also stalls INIT
    // dramatically. Matches the flash4_write_init pattern.
    if (!is_operation_in_progress(handle)) {
        if (handle->chip_id > 0) {
            flash3_check_chip_id_execute(handle);
            if (handle->response_code == RESPONSE_CODE_ERROR) {
                return;
            }
        }

        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash3_erase_execute(handle);
                delay(FLASH_ERASE_DELAY_MS);
            }
            else {
                debug("Skipping erase of memory");
                copy_to_buffer(handle->response_msg, "Skipping erase of memory");
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void flash3_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        flash_execute_command(FLASH_ENABLE_WRITE);
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);

        flash_util_verify_operation(handle, handle->data_buffer[i]);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}

void flash3_erase_execute(firestarter_handle_t* handle) {
    if (handle->address != 0) {
        debug("Sector erase");
        flash3_sector_erase(handle, handle->address);
    } else {
        debug("Chip erase");
        flash_execute_command(FLASH_ERASE);
    }
}

void flash3_sector_erase(firestarter_handle_t* handle, uint32_t sector_address) {
    byte_flip_t sector_erase_seq[6] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {sector_address, 0x30},
    };
    flash_util_byte_flipping(handle, sector_erase_seq, 6);
}


void flash3_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash3_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        uint8_t _b[4];
        _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
        _b[1] = (uint8_t)(chip_id & 0xFF);
        _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
        _b[3] = (uint8_t)(handle->chip_id & 0xFF);
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
    }
}

uint16_t flash3_get_chip_id(firestarter_handle_t* handle) {
    flash_execute_command(FLASH_ENABLE_ID);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    flash_execute_command(FLASH_DISABLE_ID);
    return chip_id;
}
