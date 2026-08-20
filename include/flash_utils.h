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
    const byte_flip FLASH_DISABLE_ID[] = {
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

    /* Phase 151 (LOCK-02) — protection-status read address & decode constants.
     * Transcribed byte-for-byte from
     * `.planning/phases/151-protection-readability-lock-status/151-SEQUENCES.md`;
     * if this file and that artifact ever disagree, the pinning legs in
     * test_val_nor_unlock.cpp / test_val_5v_page.cpp are measuring the
     * wrong thing, not this header. Both sequences are datasheet-derived —
     * infoic.xml's `config` field is the literal string "NULL" on every
     * 0x05 and 0x06 entry, so there is no machine-readable upstream to diff
     * either sequence against. The strongest available test over these
     * values is a pinned literal comparison plus this citation comment: a
     * change detector, not a correctness proof.
     *
     * Sequence A — 0x06 AMD Autoselect Sector Group Protection Verify.
     * Citation: AMD (now Infineon/Cypress) Am29F040B datasheet, Rev. F,
     * §"Autoselect Mode" (Sector Group Protection Verify at word
     * (SA)+0x02), p. 11; corroborated by Infineon AM29F002B/AM29F002NB and
     * Macronix MX29F200C T/B v2.1 p.14 §"Sector Protection Verify" via
     * `firestarter_app/doc/lockable-proms.md:34-40`. SA = 0x0000 (the
     * lowest sector) per 151-DESIGN.md §2's device-global scope decision —
     * this reports one sector's state as the device's answer, not a
     * per-sector map. x8 (byte) mode, the only mode this project's bus
     * drives. Mode entry/exit is byte-identical to FLASH_ENABLE_ID /
     * FLASH_DISABLE_ID above (confirmed in 151-SEQUENCES.md) — no new
     * byte_flip_t table for it. Addressing path: 0x0002 is well under
     * 64 KiB and is issued through handle->firestarter_get_data
     * (memory_get_data's generic mem_util_remap_address_bus path, the same
     * route flash_util_get_chip_id already uses for 0x0000/0x0001) — never
     * fu_flash_fast_address, which has no A16+ bank register and is used
     * only by the byte-flipping table writes above, whose own addresses
     * (0x5555/0x2AAA) are also under 64 KiB. */
    #define FLASH_NOR_UNLOCK_PROTECT_VERIFY_ADDR   0x0002UL
    #define FLASH_NOR_UNLOCK_PROTECT_UNPROTECTED   0x00
    #define FLASH_NOR_UNLOCK_PROTECT_PROTECTED     0x01

    /* Sequence B — 0x05 Winbond Product-ID boot-block protection status.
     * Citation: Winbond W29C020C datasheet, §"Product Identification
     * Entry/Exit" and the adjoining boot-block protection-status
     * description, p. 9 (approximate — print revision not independently
     * confirmed). Product-ID mode entry is a FINDING, not an assumption:
     * this project has no Product-ID-mode entry distinct from
     * FLASH_ENABLE_ID, and flash_util_get_chip_id already exercises that
     * exact AA/55/90 sequence on this part family today (chip_id 0xDA45,
     * confirmed on silicon) — no new byte_flip_t table for entry/exit. The
     * status-read address (0x0002) is sourced by structural analogy to that
     * already-confirmed manufacturer/device word pair, not from an
     * independently re-checked page — this is the artifact's
     * lowest-confidence citation, stated as such rather than upgraded
     * (151-SEQUENCES.md). Decode FF/FE vocabulary corroborated by
     * `firestarter_app/firestarter/eprom_operations.py:171-172`. Addressing
     * path: same reasoning as Sequence A above — 0x0002 is under 64 KiB and
     * goes through handle->firestarter_get_data, never fu_flash_fast_address. */
    #define FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR   0x0002UL
    #define FLASH_5V_PAGE_BOOT_BLOCK_UNLOCKED      0xFF
    #define FLASH_5V_PAGE_BOOT_BLOCK_LOCKED        0xFE

    void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size);
    void flash_util_verify_operation(firestarter_handle_t* handle, uint8_t expected_data);

    /* Shared AMD/JEDEC chip-ID read and mismatch check.
     * Used by flash_nor_unlock and flash_5v_page to avoid duplicating the
     * FLASH_ENABLE_ID / FLASH_DISABLE_ID command sequence.
     *
     * Phase 151 (LOCK-02): flash_util_read_in_id_mode is the same mode
     * entry/exit with a caller-supplied read address rather than the fixed
     * 0x0000/0x0001 chip-ID pair — a protect-verify read is this same
     * AMD/JEDEC ID mode, just reading a different word. It therefore lives
     * in this shared block rather than being duplicated in
     * flash_nor_unlock.cpp or flash_5v_page.cpp. */
    uint16_t flash_util_get_chip_id(firestarter_handle_t* handle);
    void flash_util_check_chip_id_execute(firestarter_handle_t* handle);
    uint8_t flash_util_read_in_id_mode(firestarter_handle_t* handle, uint32_t address);

#ifdef __cplusplus
}
#endif

#endif // __FLASH_UTILS_H__