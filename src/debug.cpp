/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "config.h"
#include "debug.h"

#ifdef SERIAL_DEBUG
#include <SoftwareSerial.h>
SoftwareSerial debugSerial(RX_DEBUG, TX_DEBUG);

void debug_setup() {
    debugSerial.begin(57600);
}

void debug_buf(const char* msg) {
    log_debug("DEBUG", msg);
}

void log_debug(const char* type, const char* msg) {
    debugSerial.print(type);
    debugSerial.print(": ");
    debugSerial.println(msg);
    debugSerial.flush();
}
#endif