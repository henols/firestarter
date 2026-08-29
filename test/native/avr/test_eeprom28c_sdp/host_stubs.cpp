/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * host stub TU for the PARKED, RED-by-design
 * test_eeprom28c_sdp suite (TRACE-02 / TRACE-04 / TRACE-06, D-01/D-02/D-09).
 * WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Identical shape to test_sdp_harness/host_stubs.cpp (plan 116-05) — this is
 * the SECOND suite that opts into the same ordered-strobe recorder layer.
 * Two suites defining the same opt-IN flag in their own, separately-linked
 * host_stubs.cpp TU is fine: [env:native] test suites are independent
 * statically-linked binaries (one per directory), never sharing a link step.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_REAL_REGISTER_UTILS: activate the ordered data+strobe
 *     recorder added by Phase 116 Plan 01. It hooks rurp_write_data_buffer +
 *     rurp_set_control_pin and records an ordered stream, suppressing exactly
 *     the six symbols the REAL include/rurp_register_utils.h +
 *     rurp_hw_rev_utils.h pair supplies below.
 *
 * PITFALL (from 116-RESEARCH.md §Code Examples / host_stubs_common.inc's own
 * doc comment): HOST_STUBS_REAL_REGISTER_UTILS MUST be defined BEFORE the
 * #include of host_stubs_common.inc — this is an opt-IN guard mirroring the
 * pre-existing HOST_STUBS_RECORD_BUS pitfall in test_val_eeprom28c/host_stubs.cpp.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS

#include "../_shared/host_stubs_common.inc"

/* D-05: production's real cache-compare + latch-strobe sequencing, instead of
 * a hand-maintained replica that could silently drift from
 * rurp_write_to_register / rurp_internal_write_to_register. */
#include "rurp_register_utils.h"

/* Pitfall 1 / Runtime State Inventory (116-RESEARCH.md): lsb_address,
 * msb_address and control_register are non-static globals
 * (rurp_register_utils.h:12-14) initialised to 0xff. They persist across
 * Unity test cases in this single binary, and the 0xff CONTROL value ORs a
 * VPP-regulator bit (CTRL_VPP_REGULATOR_ENABLE, 0x80) into the FIRST address
 * write of any case that does not reset them. Every case in this suite
 * deliberately resets the cache before driving anything — including the two
 * DIP32 "stale upper-address" cases (116-06 Task 1 / CORRECTION 3), which
 * seed CONTROL to a NON-zero value on purpose. That is a load-bearing
 * distinction: those two cases seed deliberately, every other case seeds to
 * (0x00, 0x00, 0x00) for a clean baseline.
 */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}
