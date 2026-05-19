/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "memory.h"

#include <Arduino.h>
#include <stdint.h>

#include "eprom.h"
#include "flash_type_3.h"
#include "flash_type_4.h"
#include "flash_intel.h"
#include "eeprom_28c.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_shield.h"
#include "sram.h"

#define TYPE_EPROM 1
#define TYPE_FLASH_TYPE_3 3
#define TYPE_SRAM 4
#define TYPE_FLASH_TYPE_4 5

#ifndef min
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif

void memory_read_execute(firestarter_handle_t* handle);
void memory_write_execute(firestarter_handle_t* handle);
void memory_verify_execute(firestarter_handle_t* handle);

void memory_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state);
bool memory_get_control_register(firestarter_handle_t* handle, rurp_register_t bit);
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address);
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);

uint8_t programming = 0;

void configure_memory(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_MEMORY);
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;

    switch (handle->cmd) {
        case CMD_READ:
            handle->firestarter_operation_main = memory_read_execute;
            break;
        case CMD_WRITE:
            handle->firestarter_operation_main = memory_write_execute;
            break;
        case CMD_VERIFY:
            handle->firestarter_operation_main = memory_verify_execute;
            break;
    }

    handle->firestarter_get_data = memory_get_data;
    handle->firestarter_set_data = memory_set_data;

    handle->firestarter_set_address = mem_util_set_address;

    handle->firestarter_set_control_register = memory_set_control_register;
    handle->firestarter_get_control_register = memory_get_control_register;

    mem_util_set_address(handle, 0);

    if (handle->protocol == 0x10) {
        configure_flash_intel(handle);
        return;
    }

    if (handle->protocol == 0x0D) {
        configure_eeprom28c(handle);
        return;
    }

    if (handle->protocol == 0x06) {
        configure_flash3(handle);
        return;
    }

    if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39) {
        configure_flash4(handle);
        return;
    }

    if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
        configure_eprom(handle);
        return;
    }

    if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
        handle->protocol == 0x28 || handle->protocol == 0x29) {
        configure_sram(handle);
        return;
    }

    if (handle->mem_type == TYPE_EPROM) {
        configure_eprom(handle);
        return;
    } else if (handle->mem_type == TYPE_SRAM) {
        configure_sram(handle);
        return;
    } else if (handle->mem_type == TYPE_FLASH_TYPE_3) {
        configure_flash3(handle);
        return;
    } else if (handle->mem_type == TYPE_FLASH_TYPE_4) {
        configure_flash4(handle);
        return;
    }
    LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
    handle->response_code = RESPONSE_CODE_ERROR;
}

void memory_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    rurp_register_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    rurp_register_t data = state ? control_register | (bit) : control_register & ~(bit);
    rurp_write_to_register(CONTROL_REGISTER, data);
}

bool memory_get_control_register(firestarter_handle_t* handle, rurp_register_t bit) {
    rurp_register_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    return control_register & bit;
}
rurp_register_t mem_util_calculate_lsb_register(firestarter_handle_t* handle, uint32_t address) {
    return address & 0xFF;
}

rurp_register_t mem_util_calculate_msb_register(firestarter_handle_t* handle, uint32_t address) {
    return ((address >> 8) & 0xFF);
}

rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* handle, uint32_t address) {
    rurp_register_t top_address = ((uint32_t)address >> 16) & (ADDRESS_LINE_16 | ADDRESS_LINE_17 | ADDRESS_LINE_18 | READ_WRITE);
    rurp_register_t mask = A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | REGULATOR;
    if (handle->pins < 32) {
        // VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit — preserving VPE_TO_VPP
        // would corrupt A16 for 32-pin (512KB) chips. DIP32 chips use P1_VPP_ENABLE instead.
        mask |= VPE_TO_VPP;
    }
    top_address |= rurp_read_from_register(CONTROL_REGISTER) & mask;

    if (handle->pins == 28) {
        top_address |= ADDRESS_LINE_17;
    }
    return top_address;
}

void mem_util_set_address(firestarter_handle_t* handle, uint32_t address) {
#ifdef DEBUG_ADDRESS
    LOG_DEBUG_ID_SUB_U24(DBG_ADDRESS, address);
#endif
    uint8_t lsb = mem_util_calculate_lsb_register(handle, address);
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);

    uint8_t msb = mem_util_calculate_msb_register(handle, address);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);

    rurp_register_t top_address = mem_util_calculate_top_address_register(handle, address);
    rurp_write_to_register(CONTROL_REGISTER, top_address);

#ifdef DEBUG_ADDRESS
    LOG_DEBUG_ID_SUB_U8_U8_U8(DBG_TOP_MSB_LSB, (uint8_t)top_address, msb, lsb);
#endif
}

void memory_read_execute(firestarter_handle_t* handle) {
    int buf_size = min(handle->mem_size - handle->address, DATA_BUFFER_SIZE);
    LOG_DEBUG_ID_SUB_U24(DBG_READING_FROM_ADDRESS, handle->address);
    for (int i = 0; i < buf_size; i++) {
        uint8_t data = handle->firestarter_get_data(handle, handle->address + i);
        handle->data_buffer[i] = data;
    }
    handle->data_size = buf_size;
}

uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    rurp_chip_output();
    address = mem_util_remap_address_bus(handle, address, READ_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();
    rurp_chip_enable();
    delayMicroseconds(3);
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();

    return data;
}

void memory_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }
}

void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);  // Needed for slower address changes like slow ROMs and "Power through address lines"
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);
    rurp_chip_disable();
}

void memory_verify_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
        uint8_t expected = handle->data_buffer[i];
        if (byte != expected) {
            {
                uint32_t addr = (uint32_t)(handle->address + i);
                uint8_t _b[5] = {
                    (uint8_t)expected,
                    (uint8_t)byte,
                    (uint8_t)((addr >> 16) & 0xFF),
                    (uint8_t)((addr >> 8) & 0xFF),
                    (uint8_t)(addr & 0xFF),
                };
                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);
            }
            handle->response_code = RESPONSE_CODE_ERROR;
            return;
        }
    }
}

// Utility functions
uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write) {
    bus_config_t config = handle->bus_config;
    uint32_t reorg_address = config.address_mask & address;
    if (config.address_lines[0] != 0xFF) {
        for (int i = config.matching_lines; i < ADDRESS_LINES_SIZE && config.address_lines[i] != 0xFF; i++) {
            uint32_t line_bit = (uint32_t)1 << config.address_lines[i];
            reorg_address &= ~line_bit;
            if (address & 1UL << i) {
                reorg_address |= line_bit;
            }
        }
    }
    if (config.rw_line != 0xFF) {
        reorg_address |= (uint32_t)read_write << config.rw_line;
    }

    // Set VPP line to high if VPP is not on P1
    if (config.vpp_line != 0xFF && !using_p1_as_vpp(handle)) {
        reorg_address |= 1UL << config.vpp_line;
    }

    reorg_address |= config.static_high_mask;
    return reorg_address;
}

typedef struct {
    uint32_t address;
} blank_check_progress_data_t;

#define BLANK_CHECK_CHUNK_SIZE 2048
void uint32_to_bytes(char* buffer, int pos, uint32_t value) {
    buffer[pos] = (value >> 24) & 0xFF;
    buffer[pos++] = (value >> 16) & 0xFF;
    buffer[pos++] = (value >> 8) & 0xFF;
    buffer[pos++] = value & 0xFF;
}

void mem_util_blank_check(firestarter_handle_t* handle) {
    blank_check_progress_data_t* progress_data;
    if (!is_operation_in_progress(handle)) {
        set_operation_in_progress(handle);
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));
        progress_data = (blank_check_progress_data_t*)handle->progress_data;
        progress_data->address = handle->address;
        handle->address = 0;
    } else {
        progress_data = (blank_check_progress_data_t*)handle->progress_data;
        if (handle->address >= handle->mem_size) {
            clear_operation_in_progress(handle);
            handle->address = progress_data->address;
            free(handle->progress_data);
            handle->progress_data = NULL;
            return;
        }
    }

    // for (uint32_t i = handle->address; i < handle->address + BLANK_CHECK_CHUNK_SIZE; i++) {
    uint32_t end_address = handle->address + BLANK_CHECK_CHUNK_SIZE;
    for (uint32_t i = handle->address; i < end_address && i < handle->mem_size; i++) {
        uint8_t val = handle->firestarter_get_data(handle, i);
        if (val != 0xFF) {
            {
                uint8_t _b[4] = {
                    (uint8_t)((i >> 16) & 0xFF),
                    (uint8_t)((i >> 8) & 0xFF),
                    (uint8_t)(i & 0xFF),
                    (uint8_t)val,
                };
                LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4);
            }
            handle->response_code = RESPONSE_CODE_ERROR;
            return;
        }
    }
    handle->address += BLANK_CHECK_CHUNK_SIZE;
// #define RAW_DATA_PROGRESS
#ifdef RAW_DATA_PROGRESS
    handle->response_code = RESPONSE_CODE_DATA;
    uint32_to_bytes(handle->data_buffer, 0, handle->address);
    uint32_to_bytes(handle->data_buffer, 4, handle->mem_size);
    handle->data_size = 8;
#else
    if (handle->address > handle->mem_size) {
        handle->address = handle->mem_size;
    }
    // Send progress back to the client
    LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
#endif
}
