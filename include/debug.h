/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __DEBUG_C__
#define __DEBUG_C__
#include "config.h"
#ifdef SERIAL_DEBUG
#include <Arduino.h>
#include "logging.h"

void debug_buf(const char* msg);

#define debug(msg) \
    { \
        char _buf[60]; \
        copyToBuffer(_buf, msg);\
        debug_buf(_buf); \
    }

#define debug_format(cformat, ...) \
    { \
        char _buf[60]; \
        format(_buf, cformat, __VA_ARGS__); \
        debug_buf(_buf); \
    }

#else
#define debug(msg)
#define debug_format(cformat, ...)
#define debug_setup()
#define debug_buf(msg)
#define log_debug(type, msg)
#endif

#endif