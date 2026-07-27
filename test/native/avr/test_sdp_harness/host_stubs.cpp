/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 116 Plan 05 — host stub TU for the always-green test_sdp_harness suite
 * (TRACE-01 / TRACE-03 / TRACE-04, D-03/D-05/D-06/D-07).
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_REAL_REGISTER_UTILS: activate the SECOND, independent opt-in
 *     recording layer added by Phase 116 Plan 01. This composes with (never
 *     replaces) HOST_STUBS_RECORD_BUS, used by the older test_val_eeprom28c
 *     suite. It hooks rurp_write_data_buffer + rurp_set_control_pin and
 *     records an ordered data+strobe stream, suppressing exactly the six
 *     symbols the REAL include/rurp_register_utils.h + rurp_hw_rev_utils.h
 *     pair supplies below.
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
 * write of any case that does not reset them — making the suite appear to
 * show the 5V-only 0x0D path enabling the VPP regulator, which is the exact
 * opposite of what it actually does. Every case must reset the cache
 * deliberately before driving anything.
 */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}
