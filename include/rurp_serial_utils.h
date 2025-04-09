#ifndef __RURP_SERIAL_UTILS_H__
#define __RURP_SERIAL_UTILS_H__


#ifndef SERIAL_PORT
#include <Arduino.h>
#define SERIAL_PORT Serial
#endif

#ifdef SERIAL_DEBUG
char* debug_msg_buffer;
#endif

void rurp_serial_begin(unsigned long baud) {
    SERIAL_PORT.begin(baud);
    while (!SERIAL_PORT) {
        delayMicroseconds(1);
    }
    SERIAL_PORT.flush();
    delay(1);
}

void rurp_serial_end() {
    SERIAL_PORT.end();
}

int rurp_communication_available() {
    return SERIAL_PORT.available();
}

int rurp_communication_read() {
    return SERIAL_PORT.read();
}

size_t rurp_communication_read_bytes(char* buffer, size_t length) {
    return SERIAL_PORT.readBytes(buffer, length);
}

size_t rurp_communication_write(const char* buffer, size_t size) {
    size_t bytes = SERIAL_PORT.write(buffer, size);
    SERIAL_PORT.flush();
    return bytes;
}


#ifndef RURP_CUSTOM_LOG
void rurp_log(const char* type, const char* msg) {
#else
void rurp_log_internal(const char* type, const char* msg) {
#endif
    SERIAL_PORT.print(type);
    SERIAL_PORT.print(": ");
    SERIAL_PORT.println(msg);
    SERIAL_PORT.flush();
}


#endif // __RURP_SERIAL_UTILS_H__