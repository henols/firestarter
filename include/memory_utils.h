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

    uint32_t memory_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t rw);

    void memory_blank_check(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // MEMORY_UTILS_H