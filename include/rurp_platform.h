/*
 * Firestarter platform compatibility layer.
 *
 * Common firmware includes this header instead of importing Arduino or AVR
 * headers directly. Platform backends provide the normalized timing and
 * transport surfaces used by the PROM algorithms and command processor.
 */
#ifndef __RURP_PLATFORM_H__
#define __RURP_PLATFORM_H__

#include <stddef.h>
#include <stdint.h>

#if defined(RURP_PLATFORM_PY32F071) && RURP_PLATFORM_PY32F071

#include <stdio.h>
#include <string.h>

#ifndef RURP_BOARD_NAME
#define RURP_BOARD_NAME "py32f071"
#endif

#ifndef RURP_HAS_VPP_DAC
#define RURP_HAS_VPP_DAC 1
#endif
#ifndef RURP_VPP_DAC_BITS
#define RURP_VPP_DAC_BITS 12u
#endif
#ifndef RURP_VPP_DAC_MAX_CODE
#define RURP_VPP_DAC_MAX_CODE 4095u
#endif

/* AVR flash qualifiers collapse to normal memory on memory-mapped ARM flash. */
#ifndef PROGMEM
#define PROGMEM
#endif
typedef const char *PGM_P;
#ifndef PSTR
#define PSTR(value) (value)
#endif
#ifndef F
#define F(value) (value)
#endif
#define pgm_read_byte(address) (*(const uint8_t *)(address))
#define pgm_read_word(address) (*(const uint16_t *)(address))
#define pgm_read_dword(address) (*(const uint32_t *)(address))
#define pgm_read_ptr(address) (*(const void *const *)(address))
#define memcpy_P(destination, source, length) memcpy((destination), (source), (length))
#define strcpy_P(destination, source) strcpy((destination), (source))
#define strncpy_P(destination, source, length) strncpy((destination), (source), (length))
#define strlen_P(source) strlen(source)
#define strcmp_P(left, right) strcmp((left), (right))
#define strncmp_P(left, right, length) strncmp((left), (right), (length))
#define sprintf_P sprintf

#ifndef HIGH
#define HIGH 1u
#endif
#ifndef LOW
#define LOW 0u
#endif
#ifndef INPUT
#define INPUT 0u
#endif
#ifndef OUTPUT
#define OUTPUT 1u
#endif
#ifndef A2
#define A2 2u
#endif
#ifndef A3
#define A3 3u
#endif

#ifdef __cplusplus
extern "C" {
#endif
uint32_t rurp_millis(void);
void rurp_delay_ms(uint32_t milliseconds);
void rurp_delay_us(uint32_t microseconds);

int py32_usb_available(void);
int py32_usb_read(void);
int py32_usb_peek(void);
size_t py32_usb_read_bytes(char *buffer, size_t length);
size_t py32_usb_write(const uint8_t *buffer, size_t length);
void py32_usb_flush(void);
#ifdef __cplusplus
}
#endif

#define millis() rurp_millis()
#define delay(milliseconds) rurp_delay_ms((uint32_t)(milliseconds))
#define delayMicroseconds(microseconds) rurp_delay_us((uint32_t)(microseconds))

#ifdef __cplusplus
using byte = uint8_t;

class RurpSerialPort {
public:
    void begin(unsigned long baud);
    void end();
    int available() const;
    int read();
    int peek() const;
    size_t readBytes(char *buffer, size_t length);
    size_t write(uint8_t value);
    size_t write(const uint8_t *buffer, size_t length);
    size_t write(const char *buffer, size_t length);
    size_t print(const char *text);
    size_t println(const char *text);
    void flush();
    explicit operator bool() const;
};

extern RurpSerialPort Serial;
#ifndef SERIAL_PORT
#define SERIAL_PORT Serial
#endif
#endif

#else

/* Existing builds retain their native Arduino/AVR implementation. */
#if defined(ARDUINO_AVR_UNO)
#define RURP_PLATFORM_UNO 1
#elif defined(ARDUINO_AVR_ATmega328PB)
#define RURP_PLATFORM_ATMEGA328PB 1
#elif defined(ARDUINO_AVR_LEONARDO)
#define RURP_PLATFORM_LEONARDO 1
#elif defined(RURP_PLATFORM_NATIVE)
#define RURP_PLATFORM_NATIVE_TEST 1
#endif

#ifndef RURP_HAS_VPP_DAC
#define RURP_HAS_VPP_DAC 0
#endif

#ifdef __cplusplus
#include <Arduino.h>
#endif
#include <avr/pgmspace.h>

#endif

#endif /* __RURP_PLATFORM_H__ */
