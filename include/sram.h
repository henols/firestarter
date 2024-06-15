/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef SRAM_H
#define SRAM_H

#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

    int configure_sram(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // SRAM_H