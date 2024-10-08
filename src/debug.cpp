/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "config.h"
#include "debug.h"

#ifdef SERIAL_DEBUG
#include "firestarter.h"

#include <SoftwareSerial.h>
SoftwareSerial debugSerial(RX_DEBUG, TX_DEBUG);

extern firestarter_handle_t handle;

void debug_setup() {
    debugSerial.begin(57600);
}

void debug_buf(const char* msg) {
    log_debug("DEBUG", msg);
}

void log_debug(const char* type, const char* msg) {
    // debugSerial.print(handle.state);
    // debugSerial.print(" ->  ");
    debugSerial.print(type);
    debugSerial.print(": ");
    debugSerial.println(msg);
    debugSerial.flush();
}
#endif