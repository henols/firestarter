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

/*
 * Phase 142 Plan 04 (D-10 as amended, D-12) -- DEFENSIVE, not corrective.
 * Neither of this body's two exits leaks a route today (142-RESEARCH.md's
 * exit table, E1/E2): the early return below is taken only after
 * eprom_generic_init already disabled via eprom_check_vpp's or
 * eprom_get_chip_id's own clear, and the fall-through touches no HV bit
 * that eprom_internal_erase (called a few lines below, when reached) does
 * not already clear itself. This body is renamed static and wrapped
 * anyway, because eprom_internal_erase's own assert is the ONLY write-path
 * code that asserts CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE (remapped to
 * A9 | CTRL_VPP_P1_ENABLE on a using_p1_as_vpp handle), and that assert's
 * safety rests on there being no `return` between it and its own clear --
 * a property a future edit to this body could otherwise break silently.
 * See eprom_write_init below for the public entry point and the disable
 * guarantee itself.
 */
static void eprom_internal_write_init_body(firestarter_handle_t* handle) {
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
 * Phase 142 Plan 04 (D-10 as amended, C-1, D-12) -- the single-exit
 * wrapper. Whichever exit eprom_internal_write_init_body takes (or none),
 * control comes back HERE, and this conditional is the ONLY place that
 * decides whether to clear the shared composite -- structural, not
 * remembered, so a `return` added inside the body later cannot silently
 * bypass it. Conditional on RESPONSE_CODE_ERROR, not unconditional: see
 * eprom_write_execute's own wrapper below for the named test that forced
 * that amendment and its cost if ignored -- the same reasoning applies
 * here even though (unlike eprom_write_execute) nothing in this body leaks
 * today; this wrapper's own comment above already says so.
 */
void eprom_write_init(firestarter_handle_t* handle) {
    eprom_internal_write_init_body(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
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
 * block-loop's failure path did, packs a 4-byte {addr_hi, addr_mid,
 * addr_lo, pulse_count} big-endian payload -- matching MSG_ERR_MAX_PULSES /
 * MSG_ERR_ENERGY_CAP's catalog shape (u24 address + u8 pulse count) --
 * emits it, and sets response_code.
 *
 * Phase 142 Plan 04 (VPP-02, VPP-03, resolved) -- this function's own
 * disable is now a reference to the shared EPROM_HV_ALL_OFF_MASK composite
 * (VPP-03's mask consolidation), and generalising the disable-on-error
 * guarantee to every OTHER exit in the write path is now
 * eprom_write_execute's own single-exit wrapper, below, which clears the
 * same composite structurally on every error exit -- this function is
 * simply the first of the exits that wrapper now also covers; it keeps
 * emitting the two budget-failure messages themselves, which the wrapper
 * does not.
 */
static void eprom_internal_report_budget_failure(firestarter_handle_t* handle, uint32_t address, uint8_t pulse_count, uint8_t msg_id) {
    handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
    uint8_t _b[4];
    _b[0] = (uint8_t)((address >> 16) & 0xFF);
    _b[1] = (uint8_t)((address >> 8)  & 0xFF);
    _b[2] = (uint8_t)( address        & 0xFF);
    _b[3] = pulse_count;
    LOG_ERROR_ID_BYTES(msg_id, _b, 4);
    handle->response_code = RESPONSE_CODE_ERROR;
}

/*
 * Phase 142 Plan 04 (D-05, D-06, Q4) -- the single function that resolves
 * which EPROM high-voltage route to assert for the current handle. Called
 * from both eprom_internal_write_execute_body (below) and eprom_check_vpp
 * (VPP-03's mask/selection consolidation), replacing the two byte-identical
 * hand-rolled forks this file used to carry at what were :190 and :340.
 * Declared in eprom.h (Q4: exposed, not file-static) -- see that header
 * for the full rationale and the include-edge note.
 *
 * Resolution order, exactly (D-06: FLAG_VPE_AS_VPP is a live user-facing
 * escape hatch set by no database entry -- a pure human override for the
 * 25V NMOS parts and the manual-pot workflow -- so it is checked FIRST and
 * forces the direct-VPE path on top of whatever the table says, with no
 * table read needed on that arm):
 *   1. FLAG_VPE_AS_VPP set -> CTRL_VPP_REGULATOR_ENABLE (the direct-VPE
 *      path).
 *   2. row == NULL -- configure_eprom's own refusal already makes this
 *      unreachable in practice; re-checked here anyway, matching this
 *      file's existing row==NULL precedent inside the write-execute body
 *      below -> EPROM_HV_ROUTE_MASK, failing closed toward the
 *      drop-resistor path (the safer default: a regulated ~13V rather than
 *      an unregulated direct rail).
 *   3. row->vpp_path, read ONLY via pgm_read_byte -- eprom_params.h's
 *      PROGMEM contract requires it; a direct read compiles and silently
 *      returns RAM garbage on AVR: VPP_PATH_DIRECT_VPE ->
 *      CTRL_VPP_REGULATOR_ENABLE; VPP_PATH_DROP_RESISTOR, or any
 *      unrecognised value, -> EPROM_HV_ROUTE_MASK (also fails closed
 *      toward the drop path).
 */
rurp_register_t eprom_hv_route_mask(firestarter_handle_t* handle) {
    if (is_flag_set(FLAG_VPE_AS_VPP)) {
        return CTRL_VPP_REGULATOR_ENABLE;
    }
    const eprom_params_t* row = eprom_params_for(handle->protocol);
    if (row == NULL) {
        return EPROM_HV_ROUTE_MASK;
    }
    if (pgm_read_byte(&row->vpp_path) == VPP_PATH_DIRECT_VPE) {
        return CTRL_VPP_REGULATOR_ENABLE;
    }
    return EPROM_HV_ROUTE_MASK;
}

/*
 * Phase 142 Plan 04 (D-10 as amended, C-1, D-12) -- this is everything that
 * used to be the public eprom_write_execute, renamed static and stripped of
 * its own disable logic: see the public wrapper below for the single-exit
 * disable guarantee this body now relies on. A `return` added inside here
 * in the future cannot escape that guarantee, because this body has no
 * other way out.
 */
static void eprom_internal_write_execute_body(firestarter_handle_t* handle) {
    // --- once per block (LOOP-08) --- KEPT VERBATIM; only the line number
    // moves. D-05 / VPP-01 (resolved): route selection now comes from
    // eprom_hv_route_mask (include/eprom.h), driven by the eprom_params
    // table's vpp_path column -- replacing the hand-rolled
    // protocol==0x0B||FLAG_VPE_AS_VPP fork this guard used to wrap
    // directly. configure_eprom's pulse-fallback switch remains this
    // file's one surviving tier-1 protocol-keyed site.
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        handle->firestarter_set_control_register(handle, eprom_hv_route_mask(handle), 1);
        delay(500);  // settle stays amortised once per block -- the whole of LOOP-08
    }

    // D-04 (resolved): the explicit pins>=32 clear that used to live here
    // (Phase 141) is REMOVED, not merely revised. Plan 142-02 (D-01/D-02)
    // revision-gated mem_util_calculate_top_address_register's preserve
    // mask so CTRL_VPP_VPE_DROP_ENABLE now SURVIVES a 32-pin block's
    // set_address() on Rev 2-class hardware -- an explicit clear here would
    // silently defeat that fix by re-stripping the very bit the guard
    // above just asserted, on every revision, before the fix's
    // revision-gated preserve mask ever gets a chance to matter. See
    // test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class
    // (test/native/avr/test_loop_eprom_v131) for the positive proof, and
    // test_loop08_the_28_pin_row_keeps_its_drop_bit for its unaffected
    // 28-pin partner.

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
    // Phase 142 / VPP-01 (resolved): vpp_path is read by eprom_hv_route_mask
    // above, at the top of this function -- not hoisted here, since nothing
    // below needs the raw column value again once the block's route has
    // already been asserted.
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

/*
 * Phase 142 Plan 04 (D-10 as amended, C-1, D-12) -- the single-exit wrapper
 * VPP-02 requires. Whichever of the body's four error exits is taken
 * (row == NULL; MSG_ERR_MAX_PULSES; MSG_ERR_ENERGY_CAP; MSG_ERR_VERIFY --
 * the pre-existing headline gap, which used to disable nothing at all), or
 * the success fall-through, control returns HERE, and this conditional is
 * the ONLY place that decides whether to clear the shared composite --
 * structural, so a `return` added inside the body later cannot silently
 * bypass it.
 *
 * Conditional on RESPONSE_CODE_ERROR, not unconditional -- D-10's original
 * "unconditionally" is given up here (operator-confirmed correction C-1).
 * The tiebreaker is test_loop_eprom_v131.cpp's
 * test_loop05_a_successful_block_does_not_disable_the_route, which asserts
 * a SUCCESSFUL block leaves CTRL_VPP_REGULATOR_ENABLE SET. An unconditional
 * disable would re-arm the once-per-block guard above and re-pay
 * delay(500) on the very next block too -- roughly 64s added to a 64K Uno
 * write (128 blocks) against a typical 0x07 write's ~32s total at 100us
 * pulses. The OPERATION-level disable (as opposed to this per-block loop's
 * own disable-on-error) is command_done() (firestarter.cpp:162-171), which
 * zeroes CONTROL_REGISTER unconditionally on every command exit, success
 * or abort -- plan 142-06 owes the test proving that.
 */
void eprom_write_execute(firestarter_handle_t* handle) {
    eprom_internal_write_execute_body(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
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
    handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);  // VPP-03: shared composite (was REGULATOR | A9)
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
    // D-05 / VPP-03 (resolved): route selection via eprom_hv_route_mask --
    // see eprom_internal_write_execute_body's identical call, above, for
    // the full rationale. Replaces the byte-identical
    // protocol==0x0B||FLAG_VPE_AS_VPP fork this file used to carry twice.
    handle->firestarter_set_control_register(handle, eprom_hv_route_mask(handle), 1);

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
    handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);  // VPP-03: shared composite (was REGULATOR | DROP)
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

    handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);  // VPP-03: shared composite (was REGULATOR | A9 | VPE)
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
