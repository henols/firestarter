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
    uint32_t remap_address_bus(const bus_config_t* config, uint32_t address, uint8_t rw);

#ifdef __cplusplus
}
#endif

#endif // MEMORY_H
