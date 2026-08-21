/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "flash_5v_page.h"

#include <Arduino.h>

#include "firestarter.h"
#include "flash_utils.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_pinout.h"

/* Data-driven page size derived from chip capacity (handle->mem_size).
 * W29C040 (512K = 524288) → 256; SST29EE010 (128K = 131072) → 128;
 * AT29C256 (32K = 32768) → 64. Flash4 DB chips span 32KB–512KB.
 * A fixed 256 would over-run smaller chips' 64-byte page buffers;
 * the old fixed 64 polled mid-page on W29C040 (original bug).
 * Data-driven sizing fixes W29C040 without changing effective behavior
 * for smaller chips whose native page is ≤ their derived size.
 * (Worked examples: ≤65536→64, ≤262144→128, else→256.) */
static uint32_t flash_5v_page_page_size(uint32_t mem_size) {
    if (mem_size <= 65536)  return 64;
    if (mem_size <= 262144) return 128;
    return 256;
}

void flash_5v_page_erase_execute(firestarter_handle_t* handle);
void flash_5v_page_write_init(firestarter_handle_t* handle);
void flash_5v_page_write_execute(firestarter_handle_t* handle);
void flash_5v_page_check_chip_id_execute(firestarter_handle_t* handle);
static bool flash_5v_page_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected);

uint16_t flash_5v_page_get_chip_id(firestarter_handle_t* handle);

void configure_flash_5v_page(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_FLASH4);
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = flash_5v_page_write_init;
            handle->firestarter_operation_main = flash_5v_page_write_execute;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = flash_5v_page_erase_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_CHECK_CHIP_ID:
            handle->firestarter_operation_init = NULL;
            handle->firestarter_operation_main = flash_5v_page_check_chip_id_execute;
            break;
        // Phase 151 (LOCK-02): a second query arm, modelled on
        // CMD_CHECK_CHIP_ID just above. Unlike flash_nor_unlock.cpp, this
        // file assigns no firestarter_operation_init before the switch, so
        // this arm does not null it -- there is nothing to null. The 0x01
        // force ctrl flag is deliberately not read on this path, for the
        // same reason flash_nor_unlock.cpp's CMD_LOCK_STATUS arm states:
        // elsewhere that bit means "downgrade a chip-ID mismatch to a
        // warning", this read performs no chip-ID check, and honouring the
        // bit here would give one flag two unrelated meanings (151-DESIGN.md
        // §6 / C-16).
        case CMD_LOCK_STATUS:
            handle->firestarter_operation_main = flash_5v_page_read_protection_execute;
            break;
    }
}

void flash_5v_page_write_init(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }

        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash_5v_page_erase_execute(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
    }
    // Phase 153 (152-CONTEXT.md D-07 / ERASE-02): flash4 auto-erases per
    // page during the page-write loop, so a pre-write blank check here was
    // a false precondition, not a safety net -- removed outright rather
    // than gated. FLAG_SKIP_BLANK_CHECK is consequently unread on this
    // protocol; do not restore this conditional on the grounds that the
    // bit looks orphaned.
    //
    // The erase-enable block immediately above (guarding a bulk-erase call
    // on the erase-enable flag) is a DIFFERENT thing and stays: the host
    // still clears that flag for algorithm 5, because setting it would
    // route a 12 V bulk erase onto a 5 V-only part -- a live hardware
    // hazard, not a retired one.
    //
    // D-153-05: an erase-on-write block gated this way, inside a
    // protocol's write-init, is the pattern an executor must NOT copy
    // into eeprom28c_write_init.
}

void flash_5v_page_write_execute(firestarter_handle_t* handle) {
    uint32_t page_size = flash_5v_page_page_size(handle->mem_size);
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];

        /* SDP 3-byte unlock at the start of each page load (AMD/JEDEC SDP).
         * W29C040 ships with Software Data Protection enabled; without this
         * sequence the page-buffer write is silently rejected.
         * Call per-page-START (not per-byte) — calling per-byte would abort
         * the current page load and restart it after each byte. */
        bool is_page_start = (address % page_size) == 0;
        bool is_first_byte = (i == 0);
        if (is_page_start || is_first_byte) {
            flash_execute_command(FLASH_ENABLE_WRITE);
        }

        handle->firestarter_set_data(handle, address, expected);

        bool reached_page_end = ((address + 1) % page_size) == 0;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash_5v_page_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}

static bool flash_5v_page_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    // poll the last byte written until it's correct.
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 1024; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) {
            return true;
        }
    }

    {
        uint8_t _b[5];
        _b[0] = (uint8_t)expected;
        _b[1] = (uint8_t)((address >> 16) & 0xFF);
        _b[2] = (uint8_t)((address >> 8) & 0xFF);
        _b[3] = (uint8_t)(address & 0xFF);
        _b[4] = (uint8_t)observed;
        LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT, _b, 5);
        handle->response_code = RESPONSE_CODE_ERROR;
    }
    return false;
}

void flash_5v_page_check_chip_id_execute(firestarter_handle_t* handle) {
    flash_util_check_chip_id_execute(handle);
}

// Phase 151 (LOCK-02): CMD_LOCK_STATUS operation for the 0x05 Winbond
// Product-ID boot-block family. Reads the boot-block status byte at
// FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR through the shared AMD/JEDEC
// ID-mode helper and reports the raw silicon byte plus a firmware decode,
// per 151-DESIGN.md §1. This is a 5V read -- flash_util_read_in_id_mode
// only enters/exits ID mode via FLASH_ENABLE_ID/FLASH_DISABLE_ID, so no
// VPP/VPE control-register bit is ever written on this path.
//
// Decided against emitting MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) on the
// reads-as-locked branch below, decided explicitly rather than left open
// (151-08's own instruction): that id's catalog format string reads "...
// not programmable ... write forced" -- worded for the write-path failure
// it currently has no emit site for, not for a plain status read that
// wrote nothing. Emitting it here, alongside a response_code that stays
// RESPONSE_CODE_OK for a definite decode, would misrepresent a read-only
// observation as a write-path event. The MSG_DATA_PROTECTION_STATUS DATA
// frame below already carries this observation (byte 1 = 0x01) with no
// additional catalog id needed, and leonardo's Caterina-cliff margin is
// too tight (151-08-PLAN.md's budget) to spend bytes on a second,
// semantically-mismatched emission. The id stays available, unemitted,
// for a future write-path pre-flight (CONTEXT.md's deferred "fold lock
// state into dev test diagnostic reports" idea) where "write forced"
// would actually be true.
void flash_5v_page_read_protection_execute(firestarter_handle_t* handle) {
    uint8_t raw = flash_util_read_in_id_mode(handle, FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR);
    uint8_t _b[2];
    _b[0] = raw;
    if (raw == FLASH_5V_PAGE_BOOT_BLOCK_UNLOCKED) {
        _b[1] = 0x00;
        handle->response_code = RESPONSE_CODE_OK;
    } else if (raw == FLASH_5V_PAGE_BOOT_BLOCK_LOCKED) {
        _b[1] = 0x01;
        handle->response_code = RESPONSE_CODE_OK;
    } else {
        // Unrecognised raw value: an observation the host must classify,
        // not an error this firmware can adjudicate (151-DESIGN.md §1's
        // 0xFF sentinel convention, reusing hw_get_version's precedent).
        // The DATA frame is emitted either way so the raw byte still
        // reaches the host -- never coerce this into 0x00 or 0x01.
        _b[1] = 0xFF;
        handle->response_code = RESPONSE_CODE_WARNING;
    }
    LOG_DATA_ID_BYTES(MSG_DATA_PROTECTION_STATUS, _b, 2);
}

uint16_t flash_5v_page_get_chip_id(firestarter_handle_t* handle) {
    return flash_util_get_chip_id(handle);
}

void flash_5v_page_erase_execute(firestarter_handle_t* handle) {
    uint32_t address;

    // Intial state:
    address = mem_util_remap_address_bus(handle, 0, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    rurp_chip_disable();
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 0);

    delay(2);

    //^CE -> LOW
    rurp_chip_enable();

    //^OE -> 12v
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 1);

    delay(2);
    //^WE -> LOW
    address = mem_util_remap_address_bus(handle, 0, WRITE_FLAG);
    handle->firestarter_set_address(handle, address);
    delay(20);
    //^WE -> HIGH
    address = mem_util_remap_address_bus(handle, 0, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    delay(2);

    //^CE -> LOW
    rurp_chip_disable();

    //^OE -> 12v
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 0);
}
