/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef MEMORY_UTILS_H
#define MEMORY_UTILS_H
#ifdef __cplusplus
#include "firestarter.h"
extern "C" {
#endif
    
    #define WRITE_FLAG  0
    #define READ_FLAG  1

    uint32_t m_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write);
    void m_util_blank_check(firestarter_handle_t* handle);
    void m_util_set_address(firestarter_handle_t* handle, uint32_t address);

#ifdef __cplusplus
}
#endif

#endif // MEMORY_UTILS_H