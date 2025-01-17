/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef FLASH_UTILS_H
#define FLASH_UTILS_H
#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

    typedef struct byte_flip {
        uint32_t address;
        uint8_t byte;
    } byte_flip_t;

    const byte_flip_t flash_enable_id[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x90},
    };
    const byte_flip flash_disable_id[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xF0},
    };
    const byte_flip_t flash_erase[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
    const byte_flip_t flash_enable_write[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };

    const byte_flip_t flash_enable_write_protection[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0xA0},
    };
    const byte_flip_t flash_disable_write_protection[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x20},
    };

    void flash_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size);
    void flash_verify_operation(firestarter_handle_t* handle, uint8_t expected_data);

#ifdef __cplusplus
}
#endif

#endif // FLASH_UTILS_H