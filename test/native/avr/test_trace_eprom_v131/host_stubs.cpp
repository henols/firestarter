/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 138 Plan 03 (PREP-03 / D-01 / D-02 / D-04) — host stub TU for the
 * test_trace_eprom_v131 suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_REAL_REGISTER_UTILS: the SECOND, independent opt-in
 *     recording layer (Phase 116 Plan 01). Hooks rurp_write_data_buffer +
 *     rurp_set_control_pin and records an ordered data+strobe stream,
 *     driving production's real cache-compare elision instead of a
 *     hand-maintained replica.
 *   - HOST_STUBS_RECORD_TIMING: the THIRD, independent opt-in recording
 *     layer this plan adds (Phase 138 Task 1). Stores {kind,us,seq} entries
 *     pushed by timing_push(), called from this suite's own setUp() via a
 *     fakeit .AlwaysDo hook on delay()/delayMicroseconds() — see
 *     test_trace_eprom_v131.cpp. Requires HOST_STUBS_REAL_REGISTER_UTILS
 *     (enforced by an #error in the shared .inc if it is missing), because
 *     each timing entry's interleave key is s_strobe_count at push time.
 *   - HOST_STUBS_CUSTOM_READ_DATA_BUFFER: this suite supplies its OWN
 *     stateful rurp_read_data_buffer (Task 3) that models chip read-back,
 *     so the real pre-change 27C program+verify loop (eprom_write_execute,
 *     up to NUMBER_OF_RETRIES=20 passes) converges in a handful of passes
 *     instead of exhausting every retry and overflowing the 512-entry
 *     strobe recorder. Task 2 (this file, for now) supplies only a
 *     placeholder returning 0xFF so the TU links; Task 3 replaces it with
 *     the real stateful model.
 *
 * PITFALL (from 116-RESEARCH.md §Code Examples / host_stubs_common.inc's own
 * doc comment, restated here because it applies to all three guards above):
 * every one of HOST_STUBS_REAL_REGISTER_UTILS / HOST_STUBS_RECORD_TIMING /
 * HOST_STUBS_CUSTOM_READ_DATA_BUFFER MUST be defined BEFORE the #include of
 * host_stubs_common.inc — every one of these guards reads at include time.
 *
 * CORRECTION carried from 138-PATTERNS.md item 3 (do NOT repeat
 * test_val_eprom/host_stubs.cpp's pattern here): HOST_STUBS_REAL_REGISTER_UTILS
 * already defines HOST_STUBS_CUSTOM_HW_REVISION_BLOCK (host_stubs_common.inc),
 * so the four hardware-revision stubs come from the REAL rurp_hw_rev_utils.h
 * (pulled in transitively by rurp_register_utils.h below). Additionally
 * defining the narrower, non-block hw-revision override guard here, the way
 * test_val_eprom does, would collide with that block guard. This suite does
 * not need a hardware-revision override at all (unlike test_val_eprom, which
 * needs non-REVISION_0 to reach eprom_check_vpp's VPP write) — it never
 * asserts on hardware-revision behaviour, only on the merged strobe+timing
 * stream.
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
/* Activate the timing recorder (opt-IN, Task 1). MUST precede the include,
 * and requires HOST_STUBS_REAL_REGISTER_UTILS above (its sequence key is
 * s_strobe_count, which only exists in that block). */
#define HOST_STUBS_RECORD_TIMING
/* Opt OUT of the shared .inc's default rurp_read_data_buffer (always 0), so
 * this file can supply a stateful one instead. MUST precede the include. */
#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER

#include "../_shared/host_stubs_common.inc"

/* D-02/D-05: production's real cache-compare + latch-strobe sequencing +
 * timing (delayMicroseconds(1) after every non-elided latch,
 * delayMicroseconds(4) on a VPP P1-enable set->clear transition), instead of
 * a hand-maintained replica that could silently drift from
 * rurp_write_to_register / rurp_internal_write_to_register. */
#include "rurp_register_utils.h"

/* Pitfall 1 / Runtime State Inventory (116-RESEARCH.md, restated by
 * 138-RESEARCH.md's Pitfall 5): lsb_address, msb_address and
 * control_register are non-static globals (rurp_register_utils.h:12-14)
 * initialised to 0xff. They persist across Unity test cases in this single
 * binary, and the 0xff CONTROL value ORs a VPP-regulator bit
 * (CTRL_VPP_REGULATOR_ENABLE, 0x80) into the FIRST address write of any case
 * that does not reset them. Every case must reset the cache deliberately
 * before driving anything.
 */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}

/* Task 3: stateful, index-keyed read-back model. Without this, the default
 * stub returns 0 for every read, so any non-zero target byte in the
 * synthetic block never verifies -- eprom_write_execute runs all
 * NUMBER_OF_RETRIES=20 passes and the strobe recorder overflows on an 8-byte
 * block (138-RESEARCH.md "Pitfall 4" / the blocker this plan exists to
 * solve). This is R2 from RESEARCH's two remedies: it keeps the REAL
 * memory_get_data (and therefore the real memory_set_data) in the trace,
 * unlike R1's pointer-swap, so the verify read's own bus activity is
 * captured too.
 *
 * Byte-index derivation: the byte index is the LATCHED LSB register,
 * masked to the 4-byte block size. This is valid for a block based at
 * address 0 ONLY because all three derived bus_configs (AM27C512/AM27C020/
 * AM2716) leave address bits 0-7 IDENTITY-mapped -- verified from source,
 * not assumed: mem_util_remap_address_bus's only two ways to perturb a bit
 * below the LSB byte are (a) the per-line remap loop, which starts at
 * config.matching_lines and is >= 11 for all three chips (so it never
 * touches bits 0-7), and (b) config.static_high_mask / config.vpp_line,
 * whose set bits (AM2716: bit 13; AM27C020's vpp_line 21 is skipped
 * entirely because using_p1_as_vpp() is true for that chip -- see
 * memory_utils.h) are themselves all >= bit 8. So for our four addresses
 * (0-3), the physical (remapped) address's low byte always equals the
 * logical address's low byte exactly, and reading the cached LSB register
 * (via the real rurp_read_from_register -- the same PUBLIC API production
 * code writes through, not the raw global) recovers the byte index
 * unambiguously.
 */
struct trace_readback_state_t {
    uint8_t target;
    uint8_t converge_after;
    uint8_t read_count;
};
static trace_readback_state_t s_trace_readback[4];

extern "C" void trace_readback_reset() {
    for (int i = 0; i < 4; i++) {
        s_trace_readback[i].target = 0xFF;
        s_trace_readback[i].converge_after = 0;
        s_trace_readback[i].read_count = 0;
    }
}

extern "C" void trace_readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after) {
    s_trace_readback[idx].target = target;
    s_trace_readback[idx].converge_after = converge_after;
    s_trace_readback[idx].read_count = 0;
}

extern "C" uint8_t rurp_read_data_buffer() {
    uint8_t idx = (uint8_t)(rurp_read_from_register(LEAST_SIGNIFICANT_BYTE) & 0x03);
    trace_readback_state_t* st = &s_trace_readback[idx];
    uint8_t result = (st->read_count < st->converge_after) ? 0xFF : st->target;
    st->read_count++;
    return result;
}
