/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 141 Plan 03 (LOOP-01..LOOP-08, D-10) -- host stubs for the per-byte
 * program loop suite.
 *
 * This is the SIXTH native env's suite (native_loop_v131), authored because
 * the frozen native_trace_v131 fixture goes RED by design in this phase
 * (D-10) and therefore cannot verify the loop rewrite that plans
 * 141-04/141-07/141-08 land. This file composes THREE independent,
 * pre-existing opt-in recorder layers from ../_shared/host_stubs_common.inc,
 * plus two suite-local additions (a read-back model and a logged-id
 * capture) that do not exist anywhere else in the tree:
 *
 *   - HOST_STUBS_REAL_REGISTER_UTILS (Phase 116): the ordered strobe
 *     recorder, driving production's REAL rurp_register_utils.h so the
 *     cache-compare elision and latch-strobe sequencing this suite's later
 *     assertions (plans 141-07/141-08) depend on is the genuine article,
 *     never a hand-maintained replica that could silently drift.
 *   - HOST_STUBS_RECORD_TIMING (Phase 138): the timing recorder. Its
 *     sequence key is s_strobe_count, so it can only ever compose WITH
 *     HOST_STUBS_REAL_REGISTER_UTILS above (the shared .inc fails closed
 *     with a #error if this is requested alone).
 *   - HOST_STUBS_CUSTOM_READ_DATA_BUFFER: opts this suite out of the shared
 *     .inc's default (always-0) rurp_read_data_buffer, so this file can
 *     supply its OWN stateful, 16-bit-address-keyed model instead (below) --
 *     a deliberate departure from test_trace_eprom_v131's 4-entry,
 *     LSB-masked-to-two-bits indexed model: this suite needs an UNCAPPED
 *     per-byte pulse count and a block that crosses the A16 boundary (D-09),
 *     neither of which a 4-byte, base-address-0-only index can represent.
 *
 * PITFALL, restated from host_stubs_common.inc's own doc comment and from
 * test_trace_eprom_v131/host_stubs.cpp:33-37 (138-PATTERNS.md item 3): every
 * one of the three guards above MUST be defined BEFORE the #include of
 * host_stubs_common.inc -- each is read at include time, and a #define
 * written after the include silently does nothing.
 *
 * Do NOT also define the narrower hardware-revision override guard that
 * test_val_eprom/host_stubs.cpp uses (see that file's own header comment):
 * HOST_STUBS_REAL_REGISTER_UTILS already defines the wider
 * HOST_STUBS_CUSTOM_HW_REVISION_BLOCK, so the four hardware-revision stubs
 * come from the REAL rurp_hw_rev_utils.h (pulled in transitively by
 * rurp_register_utils.h below). This suite never asserts on
 * hardware-revision behaviour, so it needs no override of that kind at all.
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
/* Activate the timing recorder (opt-IN). MUST precede the include, and
 * requires HOST_STUBS_REAL_REGISTER_UTILS above -- its sequence key is
 * s_strobe_count, which only exists in that block (enforced by an #error in
 * the shared .inc if this is requested alone). */
#define HOST_STUBS_RECORD_TIMING
/* Opt OUT of the shared .inc's default rurp_read_data_buffer (always
 * returns 0), so this file can supply the stateful, 16-bit-keyed model
 * below instead. MUST precede the include. */
#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER

#include "../_shared/host_stubs_common.inc"

/* D-02/D-05 precedent (test_trace_eprom_v131): production's real
 * cache-compare + latch-strobe sequencing + timing (delayMicroseconds(1)
 * after every non-elided latch, delayMicroseconds(4) on a VPP P1-enable
 * set->clear transition), instead of a hand-maintained replica that could
 * silently drift from rurp_write_to_register / rurp_internal_write_to_register.
 * MUST come AFTER the shared .inc -- the .inc suppresses the real
 * declarations only inside its HOST_STUBS_REAL_REGISTER_UTILS arm. */
#include "rurp_register_utils.h"

/* Pitfall (116-RESEARCH.md, restated by every suite that opts into
 * HOST_STUBS_REAL_REGISTER_UTILS -- test_trace_eprom_v131/host_stubs.cpp
 * carries the same seam under the same name): lsb_address, msb_address and
 * control_register are non-static globals (rurp_register_utils.h:12-14)
 * initialised to 0xff. They persist across Unity test cases in this single
 * binary, and the 0xff CONTROL value ORs a VPP-regulator bit
 * (CTRL_VPP_REGULATOR_ENABLE, 0x80) into the FIRST address write of any case
 * that does not reset them. Every case must reset the cache deliberately
 * before driving anything. */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}

/* ─────────────────────────────────────────────────────────────────────────
 * 16-bit-latched-address-keyed read-back model.
 *
 * Derivation of the key (source-verified against src/proms/memory.cpp, not
 * assumed): for LOOP_BUS_CONFIG_0x08 (test_loop_eprom_v131.cpp) -- copied
 * from test_trace_eprom_v131's V131_BUS_CONFIG_0x08, the tree's only 32-pin
 * config -- matching_lines is 17 and static_high_mask is 0.
 * mem_util_remap_address_bus starts from `config.address_mask & address`
 * and only perturbs bits at index >= matching_lines (here, bit 17 and up);
 * bits 0-16 are therefore left IDENTITY-mapped for every address this suite
 * or its plan-141-07/141-08 successors drive. Bit 16 (A16) is carried by
 * mem_util_calculate_top_address_register's CTRL_ADDRESS_LINE_16 bit in the
 * CONTROL top-address register, NOT by the LSB/MSB latches -- so the
 * LSB/MSB pair alone carries exactly the low 16 bits, and
 *     rurp_read_from_register(LEAST_SIGNIFICANT_BYTE)
 *     | (rurp_read_from_register(MOST_SIGNIFICANT_BYTE) << 8)
 * equals `address & 0xFFFF` for every byte of a block, including a block
 * based anywhere other than address 0 -- unlike the trace suite's
 * LSB-masked-to-two-bits index, which is valid only for a 4-byte block
 * based at 0 and would silently collapse the D-09 A16-crossing case, which
 * spans 0x00FFFE to 0x010001: as this 16-bit key, that range is 0xFFFE,
 * 0xFFFF, 0x0000, 0x0001 -- four DISTINCT keys, because the block driven
 * against them is only a handful of bytes wide, never wide enough to wrap
 * the 16-bit key space onto itself.
 *
 * Read-count-to-pulse-count mapping (the single easiest place this model
 * could be silently off by one): the loop reads FIRST (LOOP-06's skip
 * check) and only then pulses, so seeding `converge_after = N` means the
 * byte matches on read N+1, i.e. after exactly N pulses --
 * loop_readback_reads(addr) == 1 + pulses. A byte the loop skips entirely
 * under the 0xFF rule is never read at all, so its read count stays 0; an
 * already-matching byte seeded with converge_after = 0 gets exactly 1 read
 * and 0 pulses (it matches on the very first, skip-check read).
 * ───────────────────────────────────────────────────────────────────────── */

struct loop_readback_entry_t {
    uint16_t addr16;
    uint8_t target;
    uint16_t converge_after;
    uint16_t read_count;
    uint8_t seeded;
};

#define LOOP_READBACK_MAX_ENTRIES 8
static loop_readback_entry_t s_loop_readback[LOOP_READBACK_MAX_ENTRIES];

extern "C" void loop_readback_reset(void) {
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        s_loop_readback[i].addr16 = 0;
        s_loop_readback[i].target = 0xFF;
        s_loop_readback[i].converge_after = 0;
        s_loop_readback[i].read_count = 0;
        s_loop_readback[i].seeded = 0;
    }
}

extern "C" void loop_readback_seed(uint16_t addr16, uint8_t target, uint16_t converge_after) {
    int free_slot = -1;
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        if (s_loop_readback[i].seeded && s_loop_readback[i].addr16 == addr16) {
            /* Re-seeding the same address within one case: reset its read
             * counter along with the new target/converge_after. */
            s_loop_readback[i].target = target;
            s_loop_readback[i].converge_after = converge_after;
            s_loop_readback[i].read_count = 0;
            return;
        }
        if (free_slot < 0 && !s_loop_readback[i].seeded) {
            free_slot = i;
        }
    }
    if (free_slot >= 0) {
        s_loop_readback[free_slot].addr16 = addr16;
        s_loop_readback[free_slot].target = target;
        s_loop_readback[free_slot].converge_after = converge_after;
        s_loop_readback[free_slot].read_count = 0;
        s_loop_readback[free_slot].seeded = 1;
    }
    /* LOOP_READBACK_MAX_ENTRIES (8) comfortably exceeds every block this
     * suite or its plan-141-07/141-08 successors drive; a ninth seed past
     * that cap, with the table already full of distinct addresses, is not
     * reachable by any case authored in this tree. */
}

extern "C" int loop_readback_reads(uint16_t addr16) {
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        if (s_loop_readback[i].seeded && s_loop_readback[i].addr16 == addr16) {
            return (int)s_loop_readback[i].read_count;
        }
    }
    return -1;  /* never seeded -- the negative-control return value */
}

extern "C" int loop_readback_seeded_count(void) {
    int n = 0;
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        if (s_loop_readback[i].seeded) {
            n++;
        }
    }
    return n;
}

extern "C" uint8_t rurp_read_data_buffer(void) {
    uint16_t key = (uint16_t)((uint16_t)rurp_read_from_register(LEAST_SIGNIFICANT_BYTE)
                 | (uint16_t)((uint16_t)rurp_read_from_register(MOST_SIGNIFICANT_BYTE) << 8));
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        if (s_loop_readback[i].seeded && s_loop_readback[i].addr16 == key) {
            loop_readback_entry_t* e = &s_loop_readback[i];
            uint8_t result = (e->read_count < e->converge_after) ? 0xFF : e->target;
            e->read_count++;
            return result;
        }
    }
    /* Unseeded address: return 0xFF and do NOT silently create an entry --
     * the negative-control property loop_readback_seeded_count() proves. */
    return 0xFF;
}

/* ─────────────────────────────────────────────────────────────────────────
 * Logged-id capture.
 *
 * rurp_log_id (declared extern "C" inside rurp_shield.h's own extern "C"
 * block, weak-defined in src/boards/rurp_serial_utils.cpp:486) is the single
 * routing point every rurp_log_id_u8/_u16/_u24/_u32 packer (same file,
 * :495-525) calls through. A strong definition here overrides that weak
 * default and therefore captures every logged frame from any production
 * code this suite's build_src_filter compiles -- INCLUDING
 * LOG_DEBUG_ID_SUB's MSG_DEBUG entries (include/logging_id.h), so a case
 * that only cares about its own id must filter this array by id rather than
 * assume it holds only its own frame.
 * ───────────────────────────────────────────────────────────────────────── */

#define LOOP_LOGGED_ID_MAX_ENTRIES 32
#define LOOP_LOGGED_ID_MAX_PARAMS 8

struct loop_logged_id_entry_t {
    uint8_t id;
    uint8_t param_count;
    uint8_t params[LOOP_LOGGED_ID_MAX_PARAMS];
};

static loop_logged_id_entry_t s_logged_ids[LOOP_LOGGED_ID_MAX_ENTRIES];
static int s_logged_id_count = 0;
static int s_logged_id_overflow = 0;

extern "C" void clear_logged_ids(void) {
    s_logged_id_count = 0;
    s_logged_id_overflow = 0;
}

extern "C" int logged_id_count(void) {
    return s_logged_id_count;
}

extern "C" uint8_t logged_id_at(int i) {
    return s_logged_ids[i].id;
}

extern "C" uint8_t logged_id_param_count(int i) {
    return s_logged_ids[i].param_count;
}

extern "C" uint8_t logged_id_param(int i, int j) {
    return s_logged_ids[i].params[j];
}

extern "C" int logged_ids_overflowed(void) {
    return s_logged_id_overflow;
}

extern "C" void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (s_logged_id_count >= LOOP_LOGGED_ID_MAX_ENTRIES) {
        s_logged_id_overflow = 1;  /* tail dropped; prefix stays valid */
        return;
    }
    loop_logged_id_entry_t* e = &s_logged_ids[s_logged_id_count];
    uint8_t n = (param_count > LOOP_LOGGED_ID_MAX_PARAMS) ? (uint8_t)LOOP_LOGGED_ID_MAX_PARAMS : param_count;
    e->id = id;
    e->param_count = n;
    for (uint8_t j = 0; j < n; j++) {
        e->params[j] = params[j];
    }
    s_logged_id_count++;
}
