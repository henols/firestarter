/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef MEMORY_H
#define MEMORY_H

#ifdef __cplusplus
extern "C" {
#endif

#include "firestarter.h"
#include "rurp_shield.h"

#define WRITE_FLAG  0
#define READ_FLAG  1

    void configure_memory(firestarter_handle_t* handle);

    void memory_set_address(firestarter_handle_t* handle, uint32_t address);

    void memory_set_control_register(firestarter_handle_t* handle, register_t bit, bool state);

    bool memory_get_control_register(firestarter_handle_t* handle, register_t bit);

    void memory_read_data(firestarter_handle_t* handle);

    uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address);

    void memory_write_data(firestarter_handle_t* handle);

    void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);
#ifdef __cplusplus
}
#endif

#endif // MEMORY_H
