#ifndef __DEBUG_C__
#define __DEBUG_C__
#include "config.h"
#ifdef SERIAL_DEBUG

#include <SoftwareSerial.h>
#define RX_DENUG  4
#define TX_DENUG  5
SoftwareSerial debugSerial = SoftwareSerial(RX_DENUG, TX_DENUG);

void debug_setup(){
    debugSerial.begin(57600);
}

#define debug(msg) log_debug("debug", msg)

void log_debug(const char* type, const char* msg) {
  debugSerial.print(type);
  debugSerial.print(": ");
  debugSerial.println(msg);
  debugSerial.flush();
}
#else
#define debug_init()

#define debug(msg)
#define log_debug(type, msg)
#endif

#endif