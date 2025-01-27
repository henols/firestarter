/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "memory.h"
#include <Arduino.h>

#include "memory_utils.h"
#include "eprom.h"
#include "sram.h"
#include "flash_type_3.h"
#include "rurp_shield.h"
#include "logging.h"

#define TYPE_EPROM 1
#define TYPE_FLASH_TYPE_2 2
#define TYPE_FLASH_TYPE_3 3
#define TYPE_SRAM 4

void memory_read_execute(firestarter_handle_t* handle);
void memory_write_execute(firestarter_handle_t* handle);
void memory_verify_execute(firestarter_handle_t* handle);

void memory_set_address(firestarter_handle_t* handle, uint32_t address);
void memory_set_control_register(firestarter_handle_t* handle, register_t bit, bool state);
bool memory_get_control_register(firestarter_handle_t* handle, register_t bit);
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address);
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);

uint8_t programming = 0;

void configure_memory(firestarter_handle_t* handle) {
    debug("Configuring memory");
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_execute = NULL;
    handle->firestarter_operation_end = NULL;

    switch (handle->state) {
    case STATE_READ:
        handle->firestarter_operation_execute = memory_read_execute;
        break;
    case STATE_WRITE:
        handle->firestarter_operation_execute = memory_write_execute;
        break;
    case STATE_VERIFY:
        handle->firestarter_operation_execute = memory_verify_execute;
        break;
    }

    handle->firestarter_get_data = memory_get_data;
    handle->firestarter_set_data = memory_set_data;

    handle->firestarter_set_address = memory_set_address;

    handle->firestarter_set_control_register = memory_set_control_register;
    handle->firestarter_get_control_register = memory_get_control_register;
    handle->response_code = RESPONSE_CODE_OK;
#ifdef POWER_THROUGH_ADDRESS_LINES
    memory_set_address(handle, 0);
#endif
    if (handle->mem_type == TYPE_EPROM) {
        configure_eprom(handle);
        return;
    }
    else if (handle->mem_type == TYPE_SRAM) {
        configure_sram(handle);
        return;
    }
    else if (handle->mem_type == TYPE_FLASH_TYPE_3) {
        configure_flash3(handle);
        return;
    }
    format(handle->response_msg, "Memory type 0x%02x not supported", handle->mem_type);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}

void memory_set_control_register(firestarter_handle_t* handle, register_t bit, bool state) {
    register_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    register_t data = state ? control_register | (bit) : control_register & ~(bit);
    rurp_write_to_register(CONTROL_REGISTER, data);
}

bool memory_get_control_register(firestarter_handle_t* handle, register_t bit) {
    register_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    return control_register & bit;
}


void memory_set_address(firestarter_handle_t* handle, uint32_t address) {
#ifdef DEBUG_ADDRESS
    debug_format("Address 0x%06x", address);
#endif
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
#ifdef POWER_THROUGH_ADDRESS_LINES
    if (handle->pins == 24) {
        msb |= A13;
    }
#endif
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);

    register_t top_address = ((uint32_t)address >> 16) & (A16 | A17 | A18 | READ_WRITE);
    register_t mask = A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | REGULATOR;
    if (((top_address & READ_WRITE) && READ_WRITE == WRITE_FLAG) || handle->pins < 32) {
        // This breaks 128K+ ROMs since VPE_TO_VPP and A16 are shared -
        // can only write to top half etc (or write at different voltages by removing VPE_TO_VPP)
        mask |= VPE_TO_VPP;
    }
    top_address |= rurp_read_from_register(CONTROL_REGISTER) & mask;

#ifdef POWER_THROUGH_ADDRESS_LINES
    if (handle->pins == 28) {
        top_address |= A17;
    }
#endif
#ifdef DEBUG_ADDRESS
    debug_format("top msb lsb %02x %02x %02x", top_address, msb, lsb);
#endif
    rurp_write_to_register(CONTROL_REGISTER, top_address);
}

void memory_read_execute(firestarter_handle_t* handle) {
    // rurp_set_control_pin(CHIP_ENABLE, 0);
    int buf_size = min(handle->mem_size - handle->address, DATA_BUFFER_SIZE);
    debug_format("Reading from address 0x%06x", handle->address);
    for (int i = 0; i < buf_size; i++) {
        uint8_t data = handle->firestarter_get_data(handle, handle->address + i);
        // debug_format("Data 0x%02x %c", data, data);
        handle->data_buffer[i] = data;
    }
    // rurp_set_control_pin(CHIP_ENABLE, 1);
    handle->data_size = buf_size;
}

uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    // rurp_set_control_pin(OUTPUT_ENABLE, 0);
    rurp_chip_output();
    address = memory_remap_address_bus(handle, address, READ_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_set_data_as_input();
    // rurp_set_control_pin(CHIP_ENABLE , 0);
    rurp_chip_enable();
    delayMicroseconds(3);
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();

    // rurp_set_control_pin(CHIP_ENABLE , 1);
    // rurp_set_data_as_output();

    return data;
}

void memory_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }
}

void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_control_pin(OUTPUT_ENABLE, 1);
    address = memory_remap_address_bus(handle, address, WRITE_FLAG);
    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3); //Needed for slower address changes like slow ROMs and "Power through address lines"
    rurp_set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    rurp_set_control_pin(CHIP_ENABLE, 1);
}

void memory_verify_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
        uint8_t expected = handle->data_buffer[i];
        if (byte != expected) {
            format(handle->response_msg, "Expecting 0x%02x got 0x%02x at 0x%04x", expected, byte, handle->address + i);
            handle->response_code = RESPONSE_CODE_ERROR;
            return;
        }
    }
}

// Utility functions

uint32_t memory_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write) {
    bus_config_t config = handle->bus_config;
    if (config.address_lines[0] != 0xff || config.rw_line != 0xff) {

        uint32_t reorg_address = config.address_mask & address;
        for (int i = config.matching_lines; i < 19 && config.address_lines[i] != 0xFF; i++) {
            if (config.address_lines[i] != i && address & (uint32_t)1 << i) {
                reorg_address |= (uint32_t)1 << config.address_lines[i];
            }
        }
        if (config.rw_line != 0xFF) {
            reorg_address |= (uint32_t)read_write << config.rw_line;
        }
        return reorg_address;
    }
    return address;
}

void memory_blank_check(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->mem_size; i++) {
        uint8_t val = handle->firestarter_get_data(handle, i);
        if (val != 0xFF) {
            handle->response_code = RESPONSE_CODE_ERROR;
            format(handle->response_msg, "Memory is not blank, at 0x%06x, value: 0x%02x", i, val);
            return;
        }
    }
}
