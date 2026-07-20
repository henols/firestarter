#ifndef PY32F071_ARDUINO_COMPAT_H
#define PY32F071_ARDUINO_COMPAT_H

#include "rurp_platform.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifndef _BV
#define _BV(bit) (1u << (bit))
#endif
#ifndef bit_is_set
#define bit_is_set(value, bit) (((value) & _BV(bit)) != 0u)
#endif

static inline void pinMode(uint32_t pin, uint32_t mode) { (void)pin; (void)mode; }
static inline void digitalWrite(uint32_t pin, uint32_t value) { (void)pin; (void)value; }
static inline int digitalRead(uint32_t pin) { (void)pin; return 0; }
static inline void analogReference(uint32_t reference) { (void)reference; }
static inline int analogRead(uint32_t pin) { (void)pin; return 0; }

#ifndef DEFAULT
#define DEFAULT 0u
#endif

#endif
