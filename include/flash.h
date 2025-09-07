/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __FALSH__TYPE_3_H__
#define __FALSH__TYPE_3_H__

#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

    void configure_flash_amd_type(firestarter_handle_t* handle);
    void configure_flash_intel_type(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // __FALSH__TYPE_3_H__