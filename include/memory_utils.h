/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __MEMORY_UTILS_H__
#define __MEMORY_UTILS_H__
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif
#define WRITE_FLAG 0
#define READ_FLAG 1

uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write);
void mem_util_blank_check(firestarter_handle_t* handle);
void mem_util_set_address(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_lsb_register(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_msb_register(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* handle, uint32_t address);

static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins ==28 && handle->bus_config.vpp_line == VPP_P1_28_DIP);
}
static inline bool using_p21_24dip_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins ==24 && handle->bus_config.vpp_line == VPP_P21_24_DIP);
}
#ifdef __cplusplus
}
#endif

#endif  // MEMORY_UTILS_H