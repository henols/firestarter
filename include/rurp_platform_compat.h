/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_PLATFORM_COMPAT_H__
#define __RURP_PLATFORM_COMPAT_H__

#include <stdint.h>
#include <stddef.h>
#include <string.h>

/*
 * AVR keeps selected constants in a separate program-memory address space.
 * RP2040/RP2350 and native test builds use a unified address space, so the
 * AVR program-memory helpers become direct accesses on those platforms.
 */
#if defined(__AVR__)
#include <avr/pgmspace.h>
#else

#ifndef PROGMEM
#define PROGMEM
#endif

#ifndef PGM_P
#define PGM_P const char*
#endif

#ifndef PSTR
#define PSTR(value) (value)
#endif

#ifndef pgm_read_byte
#define pgm_read_byte(address) (*(const uint8_t*)(address))
#endif

#ifndef pgm_read_word
#define pgm_read_word(address) (*(const uint16_t*)(address))
#endif

#ifndef pgm_read_dword
#define pgm_read_dword(address) (*(const uint32_t*)(address))
#endif

#ifndef memcpy_P
#define memcpy_P(destination, source, size) memcpy((destination), (source), (size))
#endif

#ifndef strcpy_P
#define strcpy_P(destination, source) strcpy((destination), (source))
#endif

#ifndef strlen_P
#define strlen_P(value) strlen(value)
#endif

#ifndef strcmp_P
#define strcmp_P(left, right) strcmp((left), (right))
#endif

/* Arduino cores provide their own F() definition. Native builds do not. */
#if !defined(ARDUINO) && !defined(F)
#define F(value) (value)
#endif

#endif /* __AVR__ */

#endif /* __RURP_PLATFORM_COMPAT_H__ */
