/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __LOGGING_H__
#define __LOGGING_H__

#include <avr/pgmspace.h>

#include <Arduino.h>  // For Serial and F() macro

#include "firestarter.h"
#include "rurp_shield.h"

// Declare logging type string defined in logging.c
// LOG_OK_MSG is the only text-prefix string still used (send_ack / send_ack_const).
// All other severity bands (INIT, MAIN, END, INFO, DATA, WARN, ERROR) now emit
// ID frames via logging_id.h and no longer need a text-prefix PROGMEM string here.
extern const char LOG_OK_MSG[] PROGMEM;

// --- ACK Macros (live: send_ack called from dev_tools.cpp, send_ack_const from hardware_operations.cpp) ---
#define send_ack(msg) \
    rurp_log(LOG_OK_MSG, msg)

#define send_ack_const(msg) \
    rurp_log_P(LOG_OK_MSG, PSTR(msg))

#ifdef SERIAL_DEBUG
// Phase 8 Plan 07: debug_msg_buffer, debug_buf(), debug(), debug_format() deleted.
// All debug emit call-sites now use LOG_DEBUG_ID_SUB* from logging_id.h.
// debug_setup() retained: board-specific debug serial port init (SoftwareSerial on Uno).
// log_debug() declaration retained so uno_rurp_shield.cpp:rurp_log can call it.
void debug_setup();
void log_debug(PGM_P type, const char* msg);
#else
#define debug_setup()
#define log_debug(type, msg)
#endif

#endif  // __LOGGING_H__
