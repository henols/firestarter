#ifndef __DEBUG_C__
#define __DEBUG_C__
#include "config.h"
#ifdef SERIAL_DEBUG
#include <Arduino.h>
#include "logging.h"
#include <SoftwareSerial.h>
#define RX_DENUG  A0
#define TX_DENUG  A1
SoftwareSerial debugSerial = SoftwareSerial(RX_DENUG, TX_DENUG);

void log_debug(const char* type, const char* msg);

#define debug(msg) \
    char buf[60]; \
    copyToBuffer(buf, msg);\
    debug_buf(buf) 

#define debug_format(cformat, ...) \
    char buf[60]; \
    format(buf, cformat, __VA_ARGS__); \
    debug_buf(buf) 

void debug_setup() {
    debugSerial.begin(57600);
}

void debug_buf(const char* msg) {
    log_debug("debug", msg);
}

void log_debug(const char* type, const char* msg) {
    debugSerial.print(type);
    debugSerial.print(": ");
    debugSerial.println(msg);
    debugSerial.flush();
}


#else
#define debug(msg)
#define debug_format(cformat, ...)
#define debug_setup()
#define debug_buf(msg)
#define log_debug(type, msg)
#endif

#endif