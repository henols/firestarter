/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_TYPES_H__
#define __RURP_TYPES_H__

#include <stdint.h>

#ifndef HARDWARE_REVISION
#define rurp_register_t uint8_t
#else
#define rurp_register_t uint16_t
#endif

typedef struct rurp_configuration {
    char version[6];
    long r1;
    long r2;
    uint8_t hardware_revision;
} rurp_configuration_t;

#endif // __RURP_TYPES_H__