/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eprom.h"

#include <Arduino.h>

#include "firestarter.h"
#include "eprom_params.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "rurp_shield.h"
#include "rurp_pinout.h"
#include "operation_utils.h"


void eprom_erase_execute(firestarter_handle_t* handle);

void eprom_write_init(firestarter_handle_t* handle);
void eprom_write_execute(firestarter_handle_t* handle);
void eprom_check_chip_id_init(firestarter_handle_t* handle);
void eprom_check_chip_id_execute(firestarter_handle_t* handle);

uint16_t eprom_get_chip_id(firestarter_handle_t* handle);

void eprom_check_vpp(firestarter_handle_t* handle);

void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code);
void eprom_internal_erase(firestarter_handle_t* handle);

void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool cmd);
void (*ep_set_control_register)(struct firestarter_handle*, rurp_register_t, bool);

void eprom_generic_init(firestarter_handle_t* handle);

void configure_eprom(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EPROM);

    handle->firestarter_operation_init = eprom_generic_init;

    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eprom_write_init;
            handle->firestarter_operation_main = eprom_write_execute;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = eprom_erase_execute;
            if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
                handle->firestarter_operation_end = mem_util_blank_check;
            }
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_CHECK_CHIP_ID:
            handle->firestarter_operation_init = eprom_check_chip_id_init;
            handle->firestarter_operation_main = eprom_check_chip_id_execute;
            break;
    }

    ep_set_control_register = handle->firestarter_set_control_register;
    handle->firestarter_set_control_register = eprom_internal_set_control_register;

    // Set default pulse_delay from protocol when Python doesn't supply one
    if (handle->pulse_delay == 0) {
        switch (handle->protocol) {
            case 0x08: handle->pulse_delay = 100;  break;  // EPROM_QUICK: 100µs
            case 0x0B: handle->pulse_delay = 500;  break;  // EPROM_LEGACY: 500µs
            default:   handle->pulse_delay = 1000; break;  // EPROM_STD: 1ms
        }
    }

    // Phase 141 Plan 04 -- both refusals below run AFTER the fallback
    // switch above resolves pulse_delay: a pulse_delay of 0 would otherwise
    // compare as "not greater than the cap" vacuously, letting an
    // unresolved default slip past the D-03 check.

    // Refusal 1 (Phase 140 D-05): an unrecognised protocol fails closed
    // here rather than falling back to &EPROM_PARAMS[0], which would route
    // 13V through the drop resistor for an unknown part.
    const eprom_params_t* row = eprom_params_for(handle->protocol);
    if (row == NULL) {
        LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
        handle->response_code = RESPONSE_CODE_ERROR;
        return;
    }

    // Refusal 2 (D-03): a pulse wider than this row's per-byte
    // program-energy budget is refused pre-flight, before any high
    // voltage is enabled, and is never silently clamped -- clamping would
    // emit a pulse whose width no longer matches what the caller asked for
    // or what the trace claims. Without this, D-01's emit-then-stop rule
    // would apply a single up-to-cap VPE pulse to real silicon and then
    // report a *verify* failure -- a misconfiguration wearing a
    // silicon-failure costume. This is also the firmware-side backstop for
    // Phase 143's --pulse-us bounds, independent of host validation.
    //
    // energy_cap_us > 0 is mandatory: eprom_params.h defines 0 as
    // UNCAPPED, not "cap at zero" -- an unguarded compare would refuse
    // every 0x07/0x08 pulse (both ship energy_cap_us == 0).
    uint32_t energy_cap_us = pgm_read_dword(&row->energy_cap_us);
    if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us) {
        LOG_ERROR_ID_U32(MSG_ERR_PULSE_TOO_WIDE, handle->pulse_delay);
        handle->response_code = RESPONSE_CODE_ERROR;
        return;
    }
}

void eprom_check_chip_id_init(firestarter_handle_t* handle) {
    eprom_check_vpp(handle);
}

void eprom_check_chip_id_execute(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_CHIP_ID);
    eprom_internal_check_chip_id(handle, RESPONSE_CODE_ERROR);
}

void eprom_erase_execute(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_ERASE);
    eprom_internal_erase(handle);
}

void eprom_write_init(firestarter_handle_t* handle) {
    if(!is_operation_in_progress(handle)){
        eprom_generic_init(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
        
        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                eprom_internal_erase(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

/*
 * Phase 141 Plan 04 (LOOP-03, D-08) -- see include/eprom.h for the full
 * rationale. factor == 0 (every shipped row) always yields 0, so the
 * per-byte loop's overprogram call is inert on every live protocol; the
 * clamp below yields 0 for cap_us == 0 without a special case, since a
 * positive product always compares greater than a zero cap.
 */
uint32_t eprom_overprogram_us(uint8_t pulse_count, uint32_t pulse_us, uint8_t factor, uint32_t cap_us) {
    if (factor == 0) {
        return 0;
    }
    uint32_t product = (uint32_t)factor * pulse_count * pulse_us;
    return product > cap_us ? cap_us : product;
}

/*
 * Phase 141 Plan 04 (LOOP-05, D-04) -- the single place a per-byte program
 * budget failure is reported. Disables the VPP route exactly as the old
 * block-loop's failure path did (below, at what is today :181), packs a
 * 4-byte {addr_hi, addr_mid, addr_lo, pulse_count} big-endian payload --
 * matching MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP's catalog shape (u24
 * address + u8 pulse count) -- emits it, and sets response_code. This
 * covers only LOOP-05's own two budget-failure exits; generalising the
 * disable to every exit in the file is Phase 142 / VPP-02's job, which
 * re-verifies every exit rather than assuming this one.
 */
static void eprom_internal_report_budget_failure(firestarter_handle_t* handle, uint32_t address, uint8_t pulse_count, uint8_t msg_id) {
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);
    uint8_t _b[4];
    _b[0] = (uint8_t)((address >> 16) & 0xFF);
    _b[1] = (uint8_t)((address >> 8)  & 0xFF);
    _b[2] = (uint8_t)( address        & 0xFF);
    _b[3] = pulse_count;
    LOG_ERROR_ID_BYTES(msg_id, _b, 4);
    handle->response_code = RESPONSE_CODE_ERROR;
}

void eprom_write_execute(firestarter_handle_t* handle) {
    // --- once per block (LOOP-08) --- KEPT VERBATIM; only the line number
    // moves. Replacing this tier-1 predicate with the table's vpp_path
    // column is Phase 142 / VPP-01 -- removing it here would drop tier-1
    // to two sites.
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
            // EPROM_LEGACY: direct VPE path — no CTRL_VPP_VPE_DROP_ENABLE dropping resistor
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
        } else {
            // EPROM_STD / EPROM_QUICK: CTRL_VPP_VPE_DROP_ENABLE dropping path for precise VPP
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
        }
        delay(500);  // settle stays amortised once per block -- the whole of LOOP-08
    }

    // D-09: on a 32-pin part, mem_util_calculate_top_address_register's
    // preserve mask (memory.cpp) excludes CTRL_VPP_VPE_DROP_ENABLE whenever
    // handle->pins >= 32, so the drop route just asserted above does NOT
    // survive the first set_address() of the block -- revision-
    // independently, and not because of a bit collision (on every build
    // this project ships, CTRL_ADDRESS_LINE_16 is 0x01 and
    // CTRL_VPP_VPE_DROP_ENABLE is 0x100, two distinct bits). Clearing it
    // explicitly here changes no route selection -- the first
    // set_address() below would clear it anyway, before any pulse is
    // emitted -- but it makes the control-register state the loop runs
    // under the state that will actually hold, and makes it observable in
    // the strobe stream. Keyed on handle->pins (host-supplied, the
    // pin-count JSON field), NEVER on protocol -- a protocol == 0x08
    // predicate would be a fourth tier-1 site. Choosing the final DIP32
    // route (P1 vs drop resistor) and consolidating the mask sets is
    // Phase 142 / VPP-01 and VPP-03 -- this branch deliberately does not
    // pre-empt that choice.
    if (handle->pins >= 32) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_VPE_DROP_ENABLE, 0);
    }

    const eprom_params_t* row = eprom_params_for(handle->protocol);
    if (row == NULL) {
        // Already refused in configure_eprom (task 2) -- unreachable in
        // practice. Re-checked here so this function never dereferences a
        // NULL row on its own; returns without touching hardware further.
        return;
    }
    uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
    uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
    uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
    uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
    uint8_t  verify_mode        = pgm_read_byte(&row->verify_mode);
    uint8_t  vpp_path           = pgm_read_byte(&row->vpp_path);
    (void)vpp_path;  // hoisted for completeness; Phase 142 / VPP-01 is its consumer
    uint32_t org_delay = handle->pulse_delay;

    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint8_t expected = (uint8_t)handle->data_buffer[i];
        uint32_t addr = handle->address + i;

        // LOOP-06 skips, before any pulse. 0xFF checked first, without a
        // read: an already-erased target never needs a pulse on a UV
        // EPROM (erased state is all-ones; programming only clears bits).
        if (expected == 0xFF) {
            continue;
        }
        if (handle->firestarter_get_data(handle, addr) == expected) {
            continue;
        }

        // LOOP-01: fixed-width pulse -> verify. The width is always
        // org_delay -- it is NEVER grown, unlike the retry-escalation loop
        // this replaces.
        uint8_t pulses = 0;
        uint32_t accumulated = 0;
        for (;;) {
            handle->firestarter_set_data(handle, addr, expected);
            pulses++;
            accumulated += org_delay;  // D-02: pulse widths only
            if (handle->firestarter_get_data(handle, addr) == expected) {
                break;  // converged
            }
            // Budgets are checked only AFTER a failed verify, so a byte
            // that converges on its last permitted pulse succeeds instead
            // of failing at the boundary.
            if (pulses >= max_pulses) {
                eprom_internal_report_budget_failure(handle, addr, pulses, MSG_ERR_MAX_PULSES);
                return;
            }
            // energy_cap_us == 0 means UNCAPPED (eprom_params.h) -- without
            // this guard, 0x07/0x08 (both ship energy_cap_us == 0) would
            // abort after their very first pulse.
            if (energy_cap_us && accumulated >= energy_cap_us) {
                eprom_internal_report_budget_failure(handle, addr, pulses, MSG_ERR_ENERGY_CAP);
                return;
            }
        }

        // LOOP-03: unreachable with any shipped row (overprogram_factor is
        // 0 on all three) -- D-07's org_delay save/restore idiom. Exactly
        // one extra firestarter_set_data call at the computed width,
        // restored immediately so no failure exit between save and
        // restore can leak a modified pulse_delay into the handle.
        uint32_t op_us = eprom_overprogram_us(pulses, org_delay, overprogram_factor, overprogram_cap_us);
        if (op_us) {
            handle->pulse_delay = op_us;
            handle->firestarter_set_data(handle, addr, expected);
            handle->pulse_delay = org_delay;
        }
    }

    // verify_mode: 0x07/0x08 ship VERIFY_PER_PULSE_PLUS_FINAL -- one more
    // full-block read-and-compare pass, mirroring memory_verify_execute
    // (memory.cpp) exactly: same MSG_ERR_VERIFY id, same 5-byte payload,
    // same early return. 0x0B ships VERIFY_PER_PULSE -- no final pass.
    if (verify_mode == VERIFY_PER_PULSE_PLUS_FINAL) {
        for (uint32_t i = 0; i < handle->data_size; i++) {
            uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
            uint8_t expected = (uint8_t)handle->data_buffer[i];
            if (byte != expected) {
                uint32_t addr = handle->address + i;
                uint8_t _b[5] = {
                    expected,
                    byte,
                    (uint8_t)((addr >> 16) & 0xFF),
                    (uint8_t)((addr >> 8) & 0xFF),
                    (uint8_t)(addr & 0xFF),
                };
                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);
                handle->response_code = RESPONSE_CODE_ERROR;
                return;
            }
        }
    }
}


uint16_t eprom_get_chip_id(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_CHIP_ID);
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    delay(50);

    handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE, 1);
    delay(100);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0);
    return chip_id;
}

void eprom_check_vpp(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_VPP);
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        LOG_WARN_ID(MSG_WARN_REV0_VPP_UNSUPPORTED);
        handle->response_code = RESPONSE_CODE_WARNING;
        return;
    }
#endif
    if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
        // EPROM_LEGACY: direct VPE path
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    } else {
        // EPROM_STD / EPROM_QUICK: VPE through dropping resistor to produce VPP
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
    }

    delay(100);
    uint16_t vpp_mv = rurp_read_voltage_mv();
    LOG_DEBUG_ID_SUB_U16(DBG_CHECKING_VPP_VOLTAGE, vpp_mv);
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        {
            uint16_t _v0 = (uint16_t)((vpp_mv + 50) / 1000);
            uint16_t _v1 = (uint16_t)((((vpp_mv + 50) / 100) % 10));
            uint16_t _v2 = (uint16_t)((handle->vpp_mv + 50) / 1000);
            uint16_t _v3 = (uint16_t)((((handle->vpp_mv + 50) / 100) % 10));
            uint8_t _b[8];
            _b[0] = (uint8_t)((_v0 >> 8) & 0xFF);
            _b[1] = (uint8_t)(_v0 & 0xFF);
            _b[2] = (uint8_t)((_v1 >> 8) & 0xFF);
            _b[3] = (uint8_t)(_v1 & 0xFF);
            _b[4] = (uint8_t)((_v2 >> 8) & 0xFF);
            _b[5] = (uint8_t)(_v2 & 0xFF);
            _b[6] = (uint8_t)((_v3 >> 8) & 0xFF);
            _b[7] = (uint8_t)(_v3 & 0xFF);
            if (is_flag_set(FLAG_FORCE)) {
                LOG_WARN_ID_BYTES(MSG_WARN_VPP_HIGH, _b, 8);
                handle->response_code = RESPONSE_CODE_WARNING;
            } else {
                LOG_ERROR_ID_BYTES(MSG_ERR_VPP_HIGH, _b, 8);
                handle->response_code = RESPONSE_CODE_ERROR;
            }
        }
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        {
            uint16_t _v0 = (uint16_t)((vpp_mv + 50) / 1000);
            uint16_t _v1 = (uint16_t)((((vpp_mv + 50) / 100) % 10));
            uint16_t _v2 = (uint16_t)((handle->vpp_mv + 50) / 1000);
            uint16_t _v3 = (uint16_t)((((handle->vpp_mv + 50) / 100) % 10));
            uint8_t _b[8];
            _b[0] = (uint8_t)((_v0 >> 8) & 0xFF);
            _b[1] = (uint8_t)(_v0 & 0xFF);
            _b[2] = (uint8_t)((_v1 >> 8) & 0xFF);
            _b[3] = (uint8_t)(_v1 & 0xFF);
            _b[4] = (uint8_t)((_v2 >> 8) & 0xFF);
            _b[5] = (uint8_t)(_v2 & 0xFF);
            _b[6] = (uint8_t)((_v3 >> 8) & 0xFF);
            _b[7] = (uint8_t)(_v3 & 0xFF);
            LOG_WARN_ID_BYTES(MSG_WARN_VPP_LOW, _b, 8);
            handle->response_code = RESPONSE_CODE_WARNING;
        }
    }
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 0);
}

void eprom_internal_erase(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_INTERNAL_ERASE);
    rurp_chip_input();
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);  // Enable regulator without dropping resistor
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 1);  // Erase with VPE - assumes CTRL_VPP_VPE_DROP_ENABLE isn't set and left active previously
    delay(100);
    rurp_chip_enable();
    mem_util_delay_us(handle->pulse_delay);  // Phase 141 Plan 04 (LOOP-07/D-06 site 2): 32-bit-safe split delay
    // After the erase pulse, we should disable the chip to end the programming cycle.
    rurp_chip_disable();

    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 0);
}

void eprom_generic_init(firestarter_handle_t* handle) {
    eprom_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        return;
    }
    if (handle->chip_id > 0) {
        eprom_internal_check_chip_id(handle, is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
    }
}

void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_CHIP_ID);
    uint16_t chip_id = eprom_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        uint8_t _b[4];
        _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
        _b[1] = (uint8_t)(chip_id & 0xFF);
        _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
        _b[3] = (uint8_t)(handle->chip_id & 0xFF);
        if (error_code == RESPONSE_CODE_WARNING) {
            LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
    }
}
// Use this function to set the control register and flip CTRL_VPE_ENABLE bit to CTRL_VPE_ENABLE or CTRL_VPP_P1_ENABLE
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;
    }
    ep_set_control_register(handle, bit, state);
}

void eprom_internal_ensure_regulator_enabled(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
        delay(500);
    }
}
