/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eeprom_28c.h"

#include <Arduino.h>

#include "firestarter.h"
#include "flash_utils.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_pinout.h"

/* PAGE_SIZE 64 is a deliberate CONSERVATIVE FLOOR (D-13), not an unexamined
 * default. A mem_size-derived band table (the shape flash_5v_page.cpp's
 * flash_5v_page_page_size() uses -- READ-ONLY ANALOG, FIX-04 frozen -- NOT
 * adopted here) would be WRONG for 0x0D: the pinned infoic.xml (commit
 * a8efaedc, <database type='INFOIC2PLUS'>) records AT28MC010 at 128 KB with
 * page_size = 0x0040 (64) while AT28C010 at the SAME 128 KB density carries
 * 0x0080 (128) -- same density, different page size, so density alone
 * cannot select the right value. 64 errs SAFE: a smaller flush granularity
 * issues two legal write cycles into one physical page and can never
 * overrun a page. It is self-checking once FIX-06's read-back lands (plan
 * 117-03), which verifies whatever granularity is actually used. The real
 * per-chip value is delivered by a separate, DEFERRED phase (infoic.xml ->
 * build_db.py -> chip_database.json -> wire -> json_parser.c -> handler;
 * 117-CONTEXT.md <deferred>; not yet inserted into ROADMAP.md). */
#define PAGE_SIZE 64

// AT28C datasheet-max write-cycle time (t_WC), in milliseconds -- the
// unconditional wall-clock floor D-04 requires before polling for SDP-disable
// completion [CITED: Microchip DS20006432B section 6.6.2 p.10 / DS20006386B
// p.10, via .planning/research/SUMMARY.md]. Sibling of, not a duplicate of,
// Phase 118's AT28C_TBLC_MAX_US = 100: that constant bounds the *inter-byte*
// window inside the SDP-disable command sequence itself; this one bounds the
// *internal write cycle* that follows the sequence's last byte.
#define AT28C_TWC_MAX_MS 10

// AT28C datasheet-max byte-load cycle time (t_BLC), in microseconds -- the
// upper bound on the interval between consecutive byte loads within the
// SDP-disable command sequence (and, per the page-load citation at
// eeprom28c_write_execute below, the physically identical constraint on that
// loop too) [CITED: Microchip DS20006432B section 6.6.2 p.10 / DS20006386B
// p.10, via .planning/research/SUMMARY.md]. This is a datasheet MAXIMUM, not
// a delay to insert: post-Phase-117 eeprom28c_emit_command_sequence is a bare
// set_data loop with handle->pulse_delay = 0 and no inter-byte wait, so the
// six SDP-disable writes already run far under this budget on a 16 MHz AVR.
// Plan 118-04 turns this number into a runtime budget check (compared against
// the emit duration measured around eeprom28c_emit_command_sequence) so the
// constant is load-bearing rather than decorative -- a comment-only
// "citation" satisfying OBS-03's letter while leaving nothing to enforce it
// is exactly the v1.12 hollow-GATE-03 shape this project keeps paying down.
#define AT28C_TBLC_MAX_US 100

// DQ6 toggle bit sampled during an internal write cycle by the completion
// poll below.
#define AT28C_DQ6_TOGGLE_MASK 0x40

// Bound on the completion poll's iteration count. This is an ITERATION COUNT,
// not a millis() deadline: both native SDP suites (test_eeprom28c_sdp.cpp,
// test_sdp_harness.cpp) mock millis() to AlwaysReturn(0), so a wall-clock
// deadline loop could never terminate under a deliberately non-settling mock
// (test_case8_completion_poll_preserves_prior_severity) -- an iteration bound
// terminates regardless of what millis() reports.
#define AT28C_TOGGLE_POLL_MAX_READS 32

// Invariant completion-poll read address. AT28C256 datasheet sections
// 6.16/6.17 note 3 state any address location may be used but the address
// should not vary -- a named constant makes that invariance structural. No
// read value is ever compared against an expected or stored byte anywhere in
// the completion path below, so this is not a revival of the deleted
// (0x5555, 0x20) check.
#define EEPROM28C_TOGGLE_POLL_ADDRESS 0x5555

// FIX-06 (D-07): the data-polling bit for eeprom28c_wait_for_page_write
// below. During an internal page-write cycle, a read of the LAST BYTE
// WRITTEN returns the COMPLEMENT of that byte's DQ7; when the cycle
// completes, DQ7 reads true (matches the byte actually written). This is
// the canonical AT28C completion protocol, and it is the ONLY job
// eeprom28c_wait_for_page_write has -- it compares ONLY this one bit, never
// the whole byte. A whole-byte equality compare is the conflation FIX-06
// removes: the old conflated completion-plus-verify poll's (address, data)
// compare passed spuriously whenever the OLD byte already equalled the NEW one
// (blank 0xFF regions, unchanged bytes) -- precisely gh#11's shape.
#define AT28C_DQ7_MASK 0x80

// Bound on the page-completion poll's iteration count -- an ITERATION
// COUNT, not a millis() deadline, for the same reason as
// AT28C_TOGGLE_POLL_MAX_READS above: both native SDP suites mock millis()
// to AlwaysReturn(0), so a wall-clock deadline could never terminate under
// a deliberately non-settling mock. Preserves today's effective ceiling —
// 2000 iterations of delayMicroseconds(10), unchanged from the old
// conflated poll this replaces.
#define AT28C_PAGE_POLL_MAX_READS 2000

void eeprom28c_write_init(firestarter_handle_t* handle);
void eeprom28c_write_execute(firestarter_handle_t* handle);
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length);
static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle);
static bool eeprom28c_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected);
static bool eeprom28c_verify_page_readback(firestarter_handle_t* handle, uint32_t first_index, uint32_t last_index);

// AT28C SDP disable: 6-write sequence to magic addresses.
// D-10: kept 0x0D-local (not driving the byte-identical
// FLASH_DISABLE_WRITE_PROTECTION from the FIX-04-frozen flash_utils.h)
// so FIX-01's "0x0D-local emitter" framing stays literal and the shared
// frozen header stays untouched. The duplication is real and pre-existing --
// FLASH_DISABLE_WRITE_PROTECTION (flash_utils.h) is byte-identical, and it is
// the table Phase 116's reference emitter and always-green harness drive.
// D-11's cross-guard (plan 117-04) pins the two tables together so this
// duplication can never silently diverge from the table the Phase-116
// harness compares against. External linkage is granted here (FIX-05
// preparation) so that guard can read this PRODUCTION array directly rather
// than a transcribed test-local copy; in C++ a const array at namespace
// scope has internal linkage unless a prior declaration with external
// linkage is visible, so the extern declaration below is load-bearing.
extern const byte_flip_t EEPROM_SDP_DISABLE[6];
const byte_flip_t EEPROM_SDP_DISABLE[6] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x20},
};

void configure_eeprom28c(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EEPROM_28C);
    // AT28C page write timing requires fast consecutive writes; no pulse delay needed
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}

// A9-12V chip-identification check for AT28C EEPROM family (SAF-05).
// Mirrors eprom_get_chip_id (eprom.cpp:186-197) for the read mechanism and
// flash_intel_check_chip_id (flash_intel.cpp:146-155) for compare + response.
// Read addresses are derived from mem_size: AT28C256 = 0x7FC0/0x7FC1,
// AT28C64 = 0x1FC0/0x1FC1, etc. Caller-visible via response_code only;
// no declaration in eeprom_28c.h (static — internal linkage only).
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_CHIP_ID_28C);
    // Underflow guard: mem_size < 64 would wrap mfr_addr to ~0xFFFFFFC0 and drive
    // 12V on A9 of an arbitrary address. Canonical DB entries are >= 2 KiB, but
    // hand-crafted JSON could reach here. Treat as configuration error.
    if (handle->mem_size < 64) {
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_U32(MSG_WARN_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
        return;
    }
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    delay(50);
    handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE, 1);
    delay(100);
    uint32_t mfr_addr = handle->mem_size - 64;  // 0x7FC0 (AT28C256) / 0x1FC0 (AT28C64) / ...
    uint16_t chip_id = handle->firestarter_get_data(handle, mfr_addr) << 8;
    chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1);
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0);
    if (chip_id != handle->chip_id) {
        {
            uint8_t _b[4];
            _b[0] = (uint8_t)(((uint16_t)chip_id >> 8) & 0xFF);
            _b[1] = (uint8_t)((uint16_t)chip_id & 0xFF);
            _b[2] = (uint8_t)(((uint16_t)handle->chip_id >> 8) & 0xFF);
            _b[3] = (uint8_t)((uint16_t)handle->chip_id & 0xFF);
            if (is_flag_set(FLAG_FORCE)) {
                LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
                handle->response_code = RESPONSE_CODE_WARNING;
            } else {
                LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
                handle->response_code = RESPONSE_CODE_ERROR;
            }
        }
    }
}

// FIX-01: a 0x0D-local, remap-aware command-sequence emitter. Unlike the
// shipped flash_execute_command(...) -> flash_util_byte_flipping ->
// fu_flash_fast_address path (flash_utils.cpp, FIX-04 frozen), which writes
// only LEAST_SIGNIFICANT_BYTE/MOST_SIGNIFICANT_BYTE and never consults
// handle->bus_config or CONTROL_REGISTER, every write here goes through
// handle->firestarter_set_data -- i.e. memory_set_data (memory.cpp) -- which
// applies the full remap via mem_util_remap_address_bus and rewrites
// CONTROL_REGISTER on every address change.
//
// Explicit three-argument signature (D-06's discretion), not a
// sizeof-capturing macro like flash_execute_command: that macro implicitly
// captures `handle` from the caller's scope, which is exactly the kind of
// implicit coupling this milestone is unwinding. This shape is reusable by
// Phase 118 (report lines wrapped around the call, FLAG_SKIP_SDP_UNLOCK
// gating it) and Phase 119 (a standalone CMD_SDP_LOCK/CMD_SDP_UNLOCK arm
// driving it with a different table and no payload) without a second
// refactor.
//
// Hard constraint on this body: nothing bus-visible beyond the explicit
// data-direction call below and the set_data loop. The SDP_FIXED_* goldens
// (test/native/avr/_shared/sdp_expected.h) were recorded from
// drive_reference_emitter's bare set_data loop
// (test_sdp_harness.cpp/test_eeprom28c_sdp.cpp) -- any additional
// bus-visible call (in particular a firestarter_set_control_register
// bracket, the way flash_util_byte_flipping brackets its loop) appends
// recorded strobes and breaks cases 1-3's full-stream equality. No LOG_ call
// belongs here either: report lines are Phase 118's OBS-01 scope and must
// sit before or after the sequence, never inside it.
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    // D-12: memory_set_data (memory.cpp) never sets the data-bus direction;
    // memory_get_data sets INPUT, and eeprom28c_check_chip_id's reads sit
    // immediately upstream of this sequence -- so today's OUTPUT direction
    // is correct only incidentally, restored as a side effect of a
    // non-elided register write (rurp_register_utils.h). This explicit call
    // makes the guarantee explicit instead of incidental and restores parity
    // with what the shipped fu_flash_flip_data did (flash_utils.cpp) -- it
    // is NOT a behaviour regression. It is recorder-invisible because this
    // call is an unconditional no-op in the host stubs
    // (test/native/avr/_shared/host_stubs_common.inc), which is why no
    // SDP_FIXED_* regeneration is needed for it.
    rurp_set_data_output();
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}

// FIX-02: replaces the inverted (0x5555, 0x20) read-back -- both AT28C
// datasheets state a command-sequence byte "is not written to the device",
// so comparing a read-back against 0x20 can only pass when the sequence was
// NOT recognised. This function draws no such conclusion. It:
//   1. waits AT28C_TWC_MAX_MS unconditionally (the t_WC floor, D-04);
//   2. seeds a previous sample via one read at the invariant poll address;
//   3. polls, bounded by AT28C_TOGGLE_POLL_MAX_READS iterations, until two
//      consecutive samples agree on AT28C_DQ6_TOGGLE_MASK (settled), or the
//      bound is exhausted.
//
// D-05 (load-bearing, permanently enforced by
// test_case8_completion_poll_preserves_prior_severity): this function NEVER
// writes handle->response_code and emits NO LOG_ call, on any path. A stuck
// internal cycle stays silent here and surfaces as the first page write's
// poll failure instead (FIX-06, plan 117-03) -- one failure path for one
// fault, so clobbering severity becomes structurally impossible rather than
// merely avoided. Rejected D-05 alternatives: escalate-only-if-currently-OK
// (severity-monotonic, but a second error path for the same fault) and
// unconditional ERROR -- the latter IS today's defect, the unconditional
// handle->response_code = RESPONSE_CODE_ERROR that
// test_eeprom28c_sdp/RED-BASELINE.md's case 7 catches.
//
// Every read goes through handle->firestarter_get_data (memory_get_data).
// Note, per 117-CONTEXT.md: a read through memory_get_data folds READ_FLAG
// into DIP32_28C512_EEPROM's CONTROL bit 0x10 (CTRL_ADDRESS_LINE_17) -- the
// same stale-state mechanism RED-BASELINE.md's case 5 exploits -- and the
// next set_data call is relied on to recompute CONTROL via
// mem_util_remap_address_bus, which it does. No call here goes through
// fu_flash_data_poll() or any direct rurp_* read: that helper
// (flash_utils.cpp, FIX-04 frozen) emits four recorded strobes per read,
// which would inject entries into the stream cases 1-5 compare for full
// equality.
static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle) {
    delay(AT28C_TWC_MAX_MS);
    uint8_t previous = handle->firestarter_get_data(handle, EEPROM28C_TOGGLE_POLL_ADDRESS);
    for (uint8_t j = 0; j < AT28C_TOGGLE_POLL_MAX_READS; j++) {
        delayMicroseconds(10);
        uint8_t observed = handle->firestarter_get_data(handle, EEPROM28C_TOGGLE_POLL_ADDRESS);
        if ((observed & AT28C_DQ6_TOGGLE_MASK) == (previous & AT28C_DQ6_TOGGLE_MASK)) {
            return;
        }
        previous = observed;
    }
    // Bound exhausted -- fall out silently. No response_code write, no LOG_
    // call, on this path either (D-05).
}

void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip identity via A9-12V (SAF-05) BEFORE SDP-disable (D-08: fail-fast
    // on identity leaves the chip write-protected on mismatch).
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // Sequence length hoisted to ONE expression (Plan 118-04 Task 1): Task
    // 2's t_BLC runtime budget check derives from this exact local, so there
    // is exactly one length expression in this function -- a second copy
    // would be a silent second source of truth.
    size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);

    // OBS-01/OBS-04 (D-01, load-bearing): both report lines below are
    // UNCONDITIONAL -- emitted through the bare LOG_ID / LOG_ID_U32 macros
    // with an INFO-band id, NOT through the FLAG_VERBOSE-gated LOG_INFO_ID*
    // family. Every one of this tree's 19 existing MSG_INFO_* emissions
    // goes through LOG_INFO_ID*, and there are currently ZERO bare
    // LOG_ID*-on-an-INFO-band-id call sites anywhere in firestarter/src --
    // these two are the first. That break with house style is deliberate,
    // not an oversight: gating these lines behind FLAG_VERBOSE would leave a
    // default `firestarter write at28c256` silent, which is the exact
    // defect this phase exists to remove. Unconditional emission is also
    // what makes OBS-05's "byte-identical apart from the two report lines"
    // a real claim rather than a vacuous one -- under verbose-gating the
    // default path would emit zero new frames and OBS-05 would be trivially
    // true. A released 3.0.0b11 host that has never seen these ids degrades
    // gracefully: codec.py logs "Unknown message ID 0x.. -- catalog out of
    // date?" and drops the frame -- no crash, no garbled render.
    LOG_ID(MSG_INFO_SDP_UNLOCK);

    // Disable SDP (Software Data Protection) before writing. The sequence is
    // emitted through handle->firestarter_set_data (i.e. memory_set_data),
    // which applies the full remap via mem_util_remap_address_bus and
    // rewrites CONTROL_REGISTER on every address change -- closing both the
    // /WE-inhibit defect measured for 66 of the 84 0x0D chips
    // (flash_util_byte_flipping's fu_flash_fast_address bypasses
    // handle->bus_config entirely) and, for the 18 chips at 64 KB and above
    // on DIP32_28C512_EEPROM, the A16-A18 upper-address staleness gap
    // (FIX-03) -- both close as one by-product of this single routing
    // change, not as two separate fixes. handle->pulse_delay is already 0
    // for this protocol (see configure_eeprom28c above).
    //
    // D-05: the two microsecond-clock reads below bracket this call ONLY
    // and sit OUTSIDE eeprom28c_emit_command_sequence's body, so they
    // perturb inter-byte timing not at all -- the measured interval covers
    // the six command writes and nothing else. eeprom28c_wait_for_sdp_completion
    // (below) is deliberately excluded from the bracket: it is a fixed
    // delay(AT28C_TWC_MAX_MS) plus an iteration-bounded poll, so including
    // it would add a constant plus mock-dependent noise to the one number
    // that has engineering meaning. Elapsed is an unsigned 32-bit
    // subtraction so a wraparound of the underlying clock during the
    // window still yields a correct interval.
    uint32_t sdp_emit_start_us = micros();
    eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, sdp_seq_len);
    uint32_t sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us);

    LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us);

    // D-09: AT28C_TBLC_MAX_US (defined above) is a datasheet MAXIMUM, not a
    // delay to insert -- this runtime comparison is what turns the citation
    // into a load-bearing check rather than a decorative one. Budget is
    // derived from sdp_seq_len (never a literal 6) so it tracks the
    // sequence length automatically if EEPROM_SDP_DISABLE ever changes
    // (Phase 119 drives this same emitter with a different table). On a
    // 16 MHz AVR, with handle->pulse_delay == 0 and no inter-byte wait
    // inside eeprom28c_emit_command_sequence's loop, this branch should
    // never fire -- that is exactly what a latent invariant looks like: it
    // speaks up only if a future edit puts real work inside that loop. A
    // documentation-only constant with no enforcing check was explicitly
    // rejected -- prose-only satisfaction of OBS-03 is the hollow-gate debt
    // shape this project keeps paying down (see the v1.12 GATE-03 history).
    // No handle->response_code write on this path (D-02/D-05, permanently
    // enforced by test_case8_completion_poll_preserves_prior_severity):
    // WARN severity is carried by the message id's band alone.
    uint32_t sdp_tblc_budget_us = (uint32_t)sdp_seq_len * AT28C_TBLC_MAX_US;
    if (sdp_emit_us > sdp_tblc_budget_us) {
        LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);
    }

    // Wait for the SDP-disable internal write cycle to complete. FIX-02: the
    // old guarded read-back call at address 0x5555 comparing against terminal
    // byte 0x20 is deleted outright, not salvaged -- there is no valid form
    // of that check (see eeprom28c_wait_for_sdp_completion's comment above).
    // The replacement never aborts write-init and never touches response_code.
    eeprom28c_wait_for_sdp_completion(handle);
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}

void eeprom28c_write_execute(firestarter_handle_t* handle) {
    // Window-start index into handle->data_buffer for
    // eeprom28c_verify_page_readback below. D-08 (Claude's Discretion,
    // decision 2): the read-back covers ONLY the bytes of the CURRENT flush
    // window, not the whole physical page -- bytes a prior chunk wrote are
    // no longer in handle->data_buffer (re-reading them would either
    // fabricate an expected value or require re-deriving data the handle
    // does not hold). Each chunk's own flush already read-back-verified its
    // own bytes, so coverage of every byte THIS operation wrote is complete
    // without it. Invariant: window_start <= i < handle->data_size by
    // construction -- i is the for-loop variable below, never derived from
    // a wire field directly, so no index here can exceed data_size or
    // DATA_BUFFER_SIZE.
    uint32_t window_start = 0;
    // D-10: this per-byte set_data loop runs with handle->pulse_delay = 0 and
    // no inter-byte wait, under the IDENTICAL AT28C_TBLC_MAX_US constraint as
    // the SDP-disable command sequence (eeprom28c_emit_command_sequence,
    // above) -- both are byte-load sequences bounded by the same datasheet
    // t_BLC maximum, and this is the shared physical exposure named there.
    // The runtime budget check deliberately stays scoped to the unlock only
    // (D-09/D-10): a per-byte compare in this hot path would cost flash and
    // cycles for a surface no OBS requirement covers, and the flash delta
    // matters here -- Phase 119's LOCK-06 headroom judgement must be made
    // against Phase 117's measured +204 B, not against the research's
    // predicted saving. This comment is a breadcrumb, not a fix: gh#11 is a
    // completion/data-landed CONFLATION bug (Phase 117's finding), not a
    // sampling-rate or timing-budget bug, so whichever future phase revisits
    // gh#11 on real silicon should look at that conflation, not at this
    // constraint.
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            // D-07: completion and data-landed proof are two functions with
            // one job each. eeprom28c_wait_for_page_write answers ONLY "is
            // the internal write cycle done" (DQ7-complement poll);
            // eeprom28c_verify_page_readback answers ONLY "did the data
            // land" (per-byte read-back). The old, now-deleted, poll
            // conflated both into one whole-byte equality compare --
            // FIX-06's actual defect.
            if (!eeprom28c_wait_for_page_write(handle, address, data)) {
                return;
            }
            if (!eeprom28c_verify_page_readback(handle, window_start, i)) {
                return;
            }
            window_start = i + 1;
        }
    }
}

// FIX-06 / D-07: completion detection ONLY -- a DQ7-COMPLEMENT poll, the
// canonical AT28C completion protocol (see AT28C_DQ7_MASK above). This
// function draws NO conclusion about whether the byte's VALUE landed
// correctly -- that is eeprom28c_verify_page_readback's job, below. It
// compares only the DQ7 bit, never the whole byte: a whole-byte equality
// compare is the conflation FIX-06 removes (see AT28C_DQ7_MASK's comment
// for why that is exactly gh#11's shape).
//
// Double-read idiom (flash_util_verify_operation, flash_utils.cpp:37-39,
// READ-ONLY ANALOG, FIX-04 frozen): the DQ7 match must hold on TWO
// CONSECUTIVE reads before the poll returns done, so a single transient
// sample (a read landing mid-toggle) cannot end the poll early.
//
// Every read goes through handle->firestarter_get_data (memory_get_data) --
// never a direct rurp_* read, never fu_flash_data_poll() (flash_utils.cpp,
// FIX-04 frozen): that helper emits four recorded strobes per read, which
// would inject entries into the SDP-suite stream comparisons.
static bool eeprom28c_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < AT28C_PAGE_POLL_MAX_READS; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if ((observed & AT28C_DQ7_MASK) == (expected & AT28C_DQ7_MASK)) {
            uint8_t confirm = handle->firestarter_get_data(handle, address);
            if ((confirm & AT28C_DQ7_MASK) == (expected & AT28C_DQ7_MASK)) {
                return true;
            }
            observed = confirm;
        }
    }
    {
        uint8_t _b[5];
        _b[0] = (uint8_t)((address >> 16) & 0xFF);
        _b[1] = (uint8_t)((address >> 8) & 0xFF);
        _b[2] = (uint8_t)(address & 0xFF);
        _b[3] = (uint8_t)expected;
        _b[4] = (uint8_t)observed;
        LOG_ERROR_ID_BYTES(MSG_ERR_EEPROM_TIMEOUT, _b, 5);
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    return false;
}

// FIX-06 / D-07/D-08: data-landed proof ONLY -- a per-byte read-back over
// the CURRENT flush window (handle->data_buffer[first_index..last_index],
// inclusive), reusing memory_verify_execute's verify-mismatch payload order
// (memory.cpp:236-256): {expected, observed, addr>>16, addr>>8, addr},
// where addr is the FAILING address -- unlike the old, now-deleted, poll,
// which bare-returned mid-buffer with only the poll address and no
// per-byte attribution.
//
// D-08: this read-back is ALWAYS ON, with NO opt-out. Firmware owns the
// truth about whether its own page write landed; reporting success it
// cannot substantiate is the defect FIX-06 corrects. An opt-out would need
// a new FLAG_* value landing in lockstep across firestarter.h and the
// host's constants.py -- Phase 120 HOST-03 scope, and firmware-before-host
// forbids emitting it early. Redundancy with the host's own verify pass is
// ACCEPTED: the host's pass proves the image landed; this one proves THIS
// PAGE'S write cycle landed, and only the second can attribute a failure to
// a page.
//
// Every read goes through handle->firestarter_get_data -- the single seam
// a test's planted mock substitutes; never a direct rurp_* read.
static bool eeprom28c_verify_page_readback(firestarter_handle_t* handle, uint32_t first_index, uint32_t last_index) {
    for (uint32_t k = first_index; k <= last_index; k++) {
        uint8_t expected = (uint8_t)handle->data_buffer[k];
        uint32_t addr = handle->address + k;
        uint8_t observed = handle->firestarter_get_data(handle, addr);
        if (observed != expected) {
            {
                uint8_t _b[5];
                _b[0] = expected;
                _b[1] = observed;
                _b[2] = (uint8_t)((addr >> 16) & 0xFF);
                _b[3] = (uint8_t)((addr >> 8) & 0xFF);
                _b[4] = (uint8_t)(addr & 0xFF);
                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);
            }
            handle->response_code = RESPONSE_CODE_ERROR;
            return false;
        }
    }
    return true;
}
