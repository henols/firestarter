/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "memory.h"
#include <Arduino.h>

#include "config.h"
#include "eprom.h"
#include "sram.h"
#include "rurp_shield.h"
#include "logging.h"


#define TYPE_EPROM 1
#define TYPE_SRAM 4


void configure_memory(firestarter_handle_t* handle) {
    handle->firestarter_read_data = memory_read_data;
    handle->firestarter_write_init = NULL;
    handle->firestarter_erase = NULL;
    handle->firestarter_blank_check = NULL;

    handle->firestarter_write_data = memory_write_data;
    handle->firestarter_get_data = memory_get_data;
    handle->firestarter_set_data = memory_set_data;
    // handle->firestarter_write_to_register = memory_write_to_register;
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
    copyToBuffer(handle->response_msg, "Memory type not supported");
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}

void memory_set_control_register(firestarter_handle_t* handle, uint8_t bit, bool state) {
    uint8_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    uint8_t data = state ? control_register | (bit) : control_register & ~(bit);
    rurp_write_to_register(CONTROL_REGISTER, data);
}

bool memory_get_control_register(firestarter_handle_t* handle, uint8_t bit) {
    uint8_t control_register = rurp_read_from_register(CONTROL_REGISTER);
    return control_register & bit;
}

uint32_t remap_address_bus(const bus_config_t* config, uint32_t address, uint8_t rw) {
    uint32_t reorg_address = 0;
    for (int i = 0; i < 19 && config->address_lines[i] != 0xFF; i++) {
        if (address & (uint32_t)1 << i) {
            reorg_address |= (uint32_t)1 << config->address_lines[i];
        }
    }
    if (config->rw_line != 0xFF) {
        reorg_address |= (uint32_t)rw << config->rw_line;
    }
    return reorg_address;
}

void memory_set_address(firestarter_handle_t* handle, uint32_t address) {
#ifdef POWER_THROUGH_ADDRESS_LINES
    if (handle->pins == 24) {
        address |= (uint32_t)A13 << 8;
    }
    else if (handle->pins == 28) {
        address |= (uint32_t)A17 << 16;
    }
#endif
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);

    uint8_t top_address = ((uint32_t)address >> 16) & (A16 | A17 | A18 | RW);
    //This breaks 128K+ ROMs since VPE_TO_VPP and A16 are shared - can only write to top half etc (or write at different voltages by removing VPE_TO_VPP)
    top_address |= rurp_read_from_register(CONTROL_REGISTER) & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | REGULATOR | VPE_TO_VPP); 
    rurp_write_to_register(CONTROL_REGISTER, top_address);
}

void memory_read_data(firestarter_handle_t* handle) {
    rurp_set_control_pin(CHIP_ENABLE, 0);
    int buf_size = DATA_BUFFER_SIZE;
    for (int i = 0; i < buf_size; i++) {
        handle->data_buffer[i] = handle->firestarter_get_data(handle, handle->address + i);
    }
    rurp_set_control_pin(CHIP_ENABLE, 1);
}

uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {

    if (handle->bus_config.address_lines[0] != 0xff || handle->bus_config.rw_line != 0xff) {
        address = remap_address_bus(&handle->bus_config, address, READ_FLAG);
    }

    handle->firestarter_set_address(handle, address);
    rurp_set_data_as_input();
    rurp_set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 0);
    delayMicroseconds(3);
    uint8_t data = rurp_read_data_buffer();
    rurp_set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 1);
    rurp_set_data_as_output();

    return data;
}

void memory_write_data(firestarter_handle_t* handle) {

    for (uint32_t i = 0; i < handle->data_size; i++) {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }
    handle->response_code = RESPONSE_CODE_OK;
}

void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    if (handle->bus_config.address_lines[0] != 0xff || handle->bus_config.rw_line != 0xff) {
        address = remap_address_bus(&handle->bus_config, address, WRITE_FLAG);
    }

    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(1);
    rurp_set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    rurp_set_control_pin(CHIP_ENABLE, 1);
}
