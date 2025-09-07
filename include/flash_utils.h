/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __FLASH_UTILS_H__
#define __FLASH_UTILS_H__
#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

#define flash_execute_command(command) \
    flash_util_byte_flipping(handle, command, sizeof(command) / sizeof(command[0]));


    typedef struct byte_flip {
        uint32_t address;
        uint8_t byte;
    } byte_flip_t;

    const byte_flip_t FLASH_ENABLE_ID[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x90},
    };
    const byte_flip_t FLASH_DISABLE_ID[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xF0},
    };
    const byte_flip_t FLASH_ERASE[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
    const byte_flip_t FLASH_ENABLE_WRITE[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };

    const byte_flip_t FLASH_ENABLE_WRITE_PROTECTION[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };
    const byte_flip_t FLASH_DISABLE_WRITE_PROTECTION[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x20},
    };

    void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size);
    void flash_util_verify_operation(firestarter_handle_t* handle, uint32_t program_address, uint8_t expected_data);

#ifdef __cplusplus
}
#endif

#endif // __FLASH_UTILS_H__