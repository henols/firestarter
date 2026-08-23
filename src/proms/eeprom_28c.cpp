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

/* AT28C_PAGE_SIZE_FALLBACK 64 is a deliberate CONSERVATIVE FLOOR. A
 * mem_size-derived band table (the shape flash_5v_page.cpp's
 * flash_5v_page_page_size() uses -- READ-ONLY ANALOG, byte-frozen, NOT
 * adopted here) would be WRONG for 0x0D: the pinned infoic.xml (commit
 * a8efaedc, <database type='INFOIC2PLUS'>) records AT28MC010 at 128 KB with
 * page_size = 0x0040 (64) while AT28C010 at the SAME 128 KB density carries
 * 0x0080 (128) -- same density, different page size, so density alone
 * cannot select the right value. Both chips are in the delivered set below.
 *
 * The floor's safety for the 66 rows left on it is unproven, not disproven:
 * their page_size comes from records filed upstream under other algorithms
 * (0x07/0x0B), so we cannot assert their real page is 16 or 32 either -- the
 * page_size attribute is meaningful for the algorithm that consumes it, and
 * a record filed under 0x07/0x0B is not evidence about a 28C page buffer.
 *
 * The per-chip value for the 18 upstream-native 0x0D rows is delivered along
 * the path infoic.xml -> build_db.py -> chip_database.json -> wire ->
 * json_parser.c -> the mask resolver below -- software-proven and
 * unvalidated on silicon. AT28C_PAGE_SIZE_MAX (512) is a deliberately
 * board-invariant validation ceiling, not the buffer-size constant (512 on
 * uno/uno328pb/native, 1024 on leonardo), so the validation contract is one
 * rule on all four build environments and the native test's coverage of it
 * is total; 512 is still at or above the largest page any row in the
 * database carries (256). */
#define AT28C_PAGE_SIZE_FALLBACK 64
#define AT28C_PAGE_SIZE_MAX 512

// AT28C datasheet-max write-cycle time (t_WC), in milliseconds -- the
// unconditional wall-clock floor required before polling for SDP-disable
// completion [CITED: Microchip DS20006432B section 6.6.2 p.10 / DS20006386B
// p.10]. Sibling of, not a duplicate of, AT28C_TBLC_MAX_US = 100: that
// constant bounds the *inter-byte* window inside the SDP-disable command
// sequence itself; this one bounds the *internal write cycle* that follows
// the sequence's last byte.
#define AT28C_TWC_MAX_MS 10

// AT28C whole-device chip-erase cycle time (t_EC), in milliseconds -- the
// unconditional wall-clock floor the software six-byte chip-erase sequence
// requires after its terminal byte, before any further byte load is
// permitted [CITED: Atmel Application Note "Software Chip Erase", Rev.
// 0544B-10/98 (doc0544.pdf) -- the device internally times the erase so no
// external clocks are required, and states the Chip Erase Cycle Time t_EC as
// 20 ms Max]. Sibling of, not a duplicate of, AT28C_TWC_MAX_MS (above), which
// bounds a single internal WRITE cycle, and AT28C_TBLC_MAX_US (below), which
// bounds the inter-byte load window inside a command sequence: this one
// bounds the whole-device ERASE cycle that follows the six-byte erase code's
// last byte. The same application note forbids any byte load until the
// erase cycle completes, so this wait is an unconditional delay and not a
// poll -- the erase operation below must not reuse
// eeprom28c_wait_for_sdp_completion, which polls. No native test can prove
// this wall-clock duration: the native host stubs leave delay() unstubbed
// and record no time (test/native/avr/_shared/host_stubs_common.inc), so the
// only available proof that this delay is present at all is structural (a
// source-level assertion that the call exists), never a timing measurement.
#define AT28C_TEC_MAX_MS 20

// AT28C datasheet-max byte-load cycle time (t_BLC), in microseconds -- the
// upper bound on the interval between consecutive byte loads within the
// SDP-disable command sequence (and, per the page-load citation at
// eeprom28c_write_execute below, the physically identical constraint on that
// loop too) [CITED: Microchip DS20006432B section 6.6.2 p.10 / DS20006386B
// p.10]. This is a datasheet MAXIMUM, not a delay to insert:
// eeprom28c_emit_command_sequence is a bare set_data loop with
// handle->pulse_delay = 0 and no inter-byte wait, so the six SDP-disable
// writes already run far under this budget on a 16 MHz AVR. This number is
// also turned into a runtime budget check -- compared against the emit
// duration measured around eeprom28c_emit_command_sequence -- so the
// constant is load-bearing rather than a decorative comment-only citation
// with nothing enforcing it.
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

// The data-polling bit for eeprom28c_wait_for_page_write below. During an
// internal page-write cycle, a read of the LAST BYTE WRITTEN returns the
// COMPLEMENT of that byte's DQ7; when the cycle completes, DQ7 reads true
// (matches the byte actually written). This is the canonical AT28C
// completion protocol, and it is the ONLY job eeprom28c_wait_for_page_write
// has -- it compares ONLY this one bit, never the whole byte. A whole-byte
// equality compare is a completion-plus-verify CONFLATION: such a compare
// passes spuriously whenever the OLD byte already equals the NEW one (blank
// 0xFF regions, unchanged bytes) -- precisely gh#11's shape.
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
// The shared SDP timed-emit helper and the two standalone, payload-free
// lock/unlock operations it drives.
static void eeprom28c_emit_sdp_sequence_timed(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length,
                                               uint8_t emitted_msg_id, uint8_t done_us_msg_id);
static void eeprom28c_sdp_unlock_execute(firestarter_handle_t* handle);
static void eeprom28c_sdp_lock_execute(firestarter_handle_t* handle);
// The AN-0544B SOFTWARE six-byte chip erase -- deliberately NOT the
// datasheet's HARDWARE Chip Erase mode (12V on OE).
static void eeprom28c_erase_execute(firestarter_handle_t* handle);

// AT28C SDP disable: 6-write sequence to magic addresses. Kept 0x0D-local
// (not driving the byte-identical FLASH_DISABLE_WRITE_PROTECTION from the
// byte-frozen flash_utils.h) so this stays a 0x0D-local emitter and the
// shared frozen header stays untouched. The duplication is real and
// pre-existing -- FLASH_DISABLE_WRITE_PROTECTION (flash_utils.h) is
// byte-identical, and it is the table the native reference emitter and the
// always-green harness drive. A cross-guard pins the two tables together so
// this duplication can never silently diverge from the table that harness
// compares against. External linkage is granted here so that guard can read
// this PRODUCTION array directly rather than a transcribed test-local copy;
// in C++ a const array at namespace scope has internal linkage unless a
// prior declaration with external linkage is visible, so the extern
// declaration below is load-bearing.
extern const byte_flip_t EEPROM_SDP_DISABLE[6];
const byte_flip_t EEPROM_SDP_DISABLE[6] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x20},
};

// AT28C SDP enable: 3-write sequence to the same magic addresses, terminal
// byte 0xA0. [CITED: Atmel doc0270 rev 0270L-PEEPR-2/09 section 19 note 2 --
// the citation of record, corroborated by Microchip DS20006432B section 6.18
// note 2, whose sentence is that the Write Protect state activates at the
// end of the write cycle EVEN IF NO OTHER DATA IS LOADED.] That sentence is
// why this table carries no payload byte after the sequence and why the
// standalone lock op (below) issues no data write and no read after it.
//
// The `extern` declaration immediately below is LOAD-BEARING, not
// decorative: in C++ a namespace-scope `const` array has INTERNAL linkage
// unless a prior declaration with external linkage is visible, and the
// identity/distinctness cross-guard must be able to pin this PRODUCTION
// array directly rather than a transcribed test-local copy (same shape as
// EEPROM_SDP_DISABLE's extern above).
//
// SAFETY property, not a style point: writing 0xAA / 0x55 / 0xA0 to
// 0x5555 / 0x2AAA / 0x5555 -- the exact three writes this table holds -- is
// byte-identical to FLASH_ENABLE_WRITE (the PROTECTED-WRITE PREFIX) and to
// FLASH_ENABLE_WRITE_PROTECTION. The ONLY thing separating "lock the chip"
// from "prefix a byte write" is that NO DATA WRITE FOLLOWS this sequence.
// That makes the absence of a payload a hard safety invariant, not a
// convenience. Two consequences follow, and both are load-bearing:
//
//   1. This table is kept 0x0D-LOCAL and the flash_utils.h duplication is
//      PRESERVED rather than deduped. Once the bytes match, the array NAME
//      is the only discriminator left, so folding the three tables into one
//      would destroy real semantics. The byte-frozen flash_utils.h stays
//      untouched for the same reason.
//   2. That absence cannot be asserted by comparing tables -- comparing
//      tables can only ever prove the bytes are equal, which they are by
//      construction. It has to be asserted on the emitted STREAM instead,
//      by a no-payload case plus an exact-divergence-index case.
//
// The same rationale is recorded a second time, from the test side, in
// test/native/avr/test_sdp_harness/test_sdp_harness.cpp.
//
// Deliberate de-shaping: the three writes above are spelled as
// value-to-address correspondences, NOT as brace-wrapped address/byte
// literals, on purpose. A host-side parity gate extracts this file's tables
// with a brace-wrapped hex-pair regex and a raw brace-depth walk, and both
// mechanisms are comment-blind -- so a brace-wrapped hex pair, or a stray
// brace, anywhere in a comment here could be mistaken for part of the real
// initializer below. Keep every comment in this file free of both shapes.
extern const byte_flip_t EEPROM_SDP_ENABLE[3];
const byte_flip_t EEPROM_SDP_ENABLE[3] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0xA0},
};

void configure_eeprom28c(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EEPROM_28C);
    // AT28C page write timing requires fast consecutive writes; no pulse delay needed
    handle->pulse_delay = 0;
    // Deliberately NO default: arm in this switch. configure_memory
    // (memory.cpp:48-58) pre-sets the generic firestarter_operation_main for
    // CMD_READ/CMD_WRITE/CMD_VERIFY BEFORE calling configure_eeprom28c, so a
    // blanket default: arm here would silently overwrite that already-correct
    // main and refuse read and verify on ALL 84 0x0D chips. Separately,
    // configure_eeprom28c only ever runs for protocol 0x0D, so a default: arm
    // here could not refuse any OTHER protocol anyway.
    //
    // CMD_CHECK_CHIP_ID is the one command this protocol genuinely cannot
    // do, and it is refused generically at the operation layer by the
    // NULL-main guard -- one site instead of six, and provably total for
    // that command alone. A literal `default: -> MSG_ERR_NOT_SUPPORTED` arm
    // here is SUPERSEDED by that op-layer guard, which is the second reason
    // not to add one.
    //
    // CMD_ERASE is deliberately NOT covered by that guard: a real dispatch
    // arm for it exists below, and the arm's own proof that it actually
    // emits the AN-0544B sequence -- not merely that dispatch resolves -- is
    // what replaces the guard for that one cell.
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_ERASE:
            handle->firestarter_operation_main = eeprom28c_erase_execute;
            break;
        case CMD_SDP_UNLOCK:
            handle->firestarter_operation_main = eeprom28c_sdp_unlock_execute;
            break;
        case CMD_SDP_LOCK:
            handle->firestarter_operation_main = eeprom28c_sdp_lock_execute;
            break;
    }
}

// A9-12V chip-identification check for the AT28C EEPROM family.
// Mirrors eprom_get_chip_id (eprom.cpp:186-197) for the read mechanism and
// flash_intel_check_chip_id (flash_intel.cpp) for compare + response.
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
    mem_util_report_chip_id(handle, chip_id, is_flag_set(FLAG_FORCE));
}

// A 0x0D-local, remap-aware command-sequence emitter. Unlike the shipped
// flash_execute_command(...) -> flash_util_byte_flipping ->
// fu_flash_fast_address path (flash_utils.cpp, byte-frozen), which writes
// only LEAST_SIGNIFICANT_BYTE/MOST_SIGNIFICANT_BYTE and never consults
// handle->bus_config or CONTROL_REGISTER, every write here goes through
// handle->firestarter_set_data -- i.e. memory_set_data (memory.cpp) -- which
// applies the full remap via mem_util_remap_address_bus and rewrites
// CONTROL_REGISTER on every address change.
//
// Explicit three-argument signature, not a sizeof-capturing macro like
// flash_execute_command: that macro implicitly captures `handle` from the
// caller's scope, which is exactly the kind of implicit coupling this file
// avoids. The explicit shape is what lets both of today's callers share one
// emitter -- eeprom28c_write_init's auto-unlock (report lines wrapped around
// the call, FLAG_SKIP_SDP_UNLOCK gating it) and the standalone
// CMD_SDP_LOCK/CMD_SDP_UNLOCK ops (a different table, no payload).
//
// Hard constraint on this body: nothing bus-visible beyond the explicit
// data-direction call below and the set_data loop. The SDP_FIXED_* goldens
// (test/native/avr/_shared/sdp_expected.h) were recorded from
// drive_reference_emitter's bare set_data loop
// (test_sdp_harness.cpp/test_eeprom28c_sdp.cpp) -- any additional
// bus-visible call (in particular a firestarter_set_control_register
// bracket, the way flash_util_byte_flipping brackets its loop) appends
// recorded strobes and breaks cases 1-3's full-stream equality. No LOG_ call
// belongs here either: report lines must sit before or after the sequence,
// never inside it.
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    // memory_set_data (memory.cpp) never sets the data-bus direction;
    // memory_get_data sets INPUT, and eeprom28c_check_chip_id's reads sit
    // immediately upstream of this sequence -- so without the call below the
    // OUTPUT direction would be correct only incidentally, restored as a
    // side effect of a non-elided register write
    // (rurp_register_utils.h). This explicit call makes the guarantee
    // explicit instead of incidental and matches what the shipped
    // fu_flash_flip_data did (flash_utils.cpp) -- it is NOT a behaviour
    // regression. It is recorder-invisible because this call is an
    // unconditional no-op in the host stubs
    // (test/native/avr/_shared/host_stubs_common.inc), which is why no
    // SDP_FIXED_* regeneration is needed for it.
    rurp_set_data_output();
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}

// NO read-back compare against a command-sequence byte belongs here: both
// AT28C datasheets state that such a byte "is not written to the device", so
// comparing a read-back at (0x5555, 0x20) against 0x20 can only pass when
// the sequence was NOT recognised -- an inverted check. This function draws
// no such conclusion. It:
//   1. waits AT28C_TWC_MAX_MS unconditionally (the t_WC floor);
//   2. seeds a previous sample via one read at the invariant poll address;
//   3. polls, bounded by AT28C_TOGGLE_POLL_MAX_READS iterations, until two
//      consecutive samples agree on AT28C_DQ6_TOGGLE_MASK (settled), or the
//      bound is exhausted.
//
// LOAD-BEARING, and permanently enforced by
// test_case8_completion_poll_preserves_prior_severity: this function NEVER
// writes handle->response_code and emits NO LOG_ call, on any path. A stuck
// internal cycle stays silent here and surfaces as the first page write's
// poll failure instead -- one failure path for one fault, so clobbering
// severity becomes structurally impossible rather than merely avoided. Two
// alternatives were considered and rejected: escalate-only-if-currently-OK
// (severity-monotonic, but a second error path for the same fault), and an
// unconditional handle->response_code = RESPONSE_CODE_ERROR here, which is
// exactly the defect this shape replaced.
//
// Every read goes through handle->firestarter_get_data (memory_get_data).
// Note: a read through memory_get_data folds READ_FLAG into
// DIP32_28C512_EEPROM's CONTROL bit 0x10 (CTRL_ADDRESS_LINE_17) -- a
// stale-state mechanism the native SDP suite deliberately exercises -- and
// the next set_data call is relied on to recompute CONTROL via
// mem_util_remap_address_bus, which it does. No call here goes through
// fu_flash_data_poll() or any direct rurp_* read: that helper
// (flash_utils.cpp, byte-frozen) emits four recorded strobes per read, which
// would inject entries into the stream cases 1-5 compare for full
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
    // call, on this path either.
}

// Shared micros()-bracket-plus-t_BLC-budget-check helper for BOTH SDP
// command sequences -- the six-write disable (EEPROM_SDP_DISABLE) and the
// three-write enable (EEPROM_SDP_ENABLE, above). It is shared by
// eeprom28c_write_init's auto-unlock and by the standalone
// eeprom28c_sdp_unlock_execute / eeprom28c_sdp_lock_execute ops below, so
// all three get the identical report-pair shape, the identical micros()
// bracket and the identical length-derived budget check without a second,
// drifting copy of any of the three.
//
// The two micros() reads bracket ONLY the call to
// eeprom28c_emit_command_sequence -- they sit OUTSIDE that function's body,
// so they perturb inter-byte timing not at all. The completion wait that
// follows a sequence (the bounded DQ6 toggle poll for the unlock, a plain
// t_WC delay for the lock -- two DIFFERENT waits) is deliberately EXCLUDED
// from this bracket and stays at each call site: check_no_log_in_sdp_window.py
// requires a wait anchor positioned after the emit anchor inside
// eeprom28c_write_init's own body, and folding either wait shape into this
// helper would either break that gate's anchor search or force one wait
// shape onto both sequences.
//
// The budget is derived from `length` -- NEVER a literal 3 or 6 -- so it
// tracks whichever sequence is passed automatically: 6 writes gives 600 us
// for the unlock, 3 gives 300 us for the lock. A bench run measured 572 us
// against the unlock's 600 us budget on a real Leonardo -- a 4.7% margin --
// so this check is load-bearing on both paths, not a latent invariant that
// never fires.
//
// This function's body contains LOG_ID / LOG_ID_U32 / LOG_WARN_ID_U32 calls
// BY DESIGN and must NEVER be added as a third scanned window in
// check_no_log_in_sdp_window.py -- the real inter-byte SDP timing window
// remains eeprom28c_emit_command_sequence's body (still shared by both
// sequences, still scanned); this helper's body is the report/measurement
// wrapper AROUND that call, not the timing window itself.
//
// No handle->response_code write anywhere in this helper (permanently
// enforced by test_case8_completion_poll_preserves_prior_severity): WARN
// severity is carried by the message id's band alone.
static void eeprom28c_emit_sdp_sequence_timed(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length,
                                               uint8_t emitted_msg_id, uint8_t done_us_msg_id) {
    LOG_ID(emitted_msg_id);
    uint32_t sdp_emit_start_us = micros();
    eeprom28c_emit_command_sequence(handle, sequence, length);
    uint32_t sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us);
    LOG_ID_U32(done_us_msg_id, sdp_emit_us);

    uint32_t sdp_tblc_budget_us = (uint32_t)length * AT28C_TBLC_MAX_US;
    if (sdp_emit_us > sdp_tblc_budget_us) {
        LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);
    }
}

// The standalone unlock reuses the existing ids (MSG_INFO_SDP_UNLOCK /
// MSG_INFO_SDP_UNLOCK_DONE_US) so an SDP unlock reads identically on the
// wire however it was triggered -- from eeprom28c_write_init's auto-unlock or
// from this standalone CMD_SDP_UNLOCK op. Reusing the SAME completion wait
// (eeprom28c_wait_for_sdp_completion) is what makes the standalone unlock's
// emitted stream byte-identical to the auto-unlock's -- an equality the
// native suite asserts. This op writes no handle->response_code.
static void eeprom28c_sdp_unlock_execute(firestarter_handle_t* handle) {
    size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);
    eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE, sdp_seq_len, MSG_INFO_SDP_UNLOCK,
                                       MSG_INFO_SDP_UNLOCK_DONE_US);
    eeprom28c_wait_for_sdp_completion(handle);
}

// The lock is exactly three writes plus the t_WC delay, and NOTHING else. It
// deliberately does NOT call eeprom28c_wait_for_sdp_completion: that
// function is the t_WC delay PLUS up to AT28C_TOGGLE_POLL_MAX_READS reads
// through handle->firestarter_get_data, and a memory_get_data read folds
// READ_FLAG into DIP32_28C512_EEPROM's CONTROL bit 0x10 -- so reusing it
// would inject read-induced CONTROL churn into all four lock goldens, for an
// outcome that is never reported anyway. The DQ6 toggle poll's outcome must
// never be reported as lock evidence even if it WERE run here: a settled
// toggle bit proves a write cycle finished, not that protection latched, and
// that is the deleted inverted-read-back mistake in a new costume. This op
// writes no handle->response_code and contains no read call, no completion
// poll and no data write.
static void eeprom28c_sdp_lock_execute(firestarter_handle_t* handle) {
    size_t sdp_seq_len = sizeof(EEPROM_SDP_ENABLE) / sizeof(EEPROM_SDP_ENABLE[0]);
    eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_ENABLE, sdp_seq_len, MSG_INFO_SDP_LOCK,
                                       MSG_INFO_SDP_LOCK_DONE_US);
    delay(AT28C_TWC_MAX_MS);
}

// The AN-0544B SOFTWARE six-byte chip erase. [CITED: Atmel Application Note
// "Software Chip Erase", Rev. 0544B-10/98 (doc0544.pdf)] -- the six load
// commands below drive every byte in the device to 0xFF, the device
// internally times the erase cycle (t_EC, AT28C_TEC_MAX_MS, 20 ms Max) so no
// external clock or completion poll is required or permitted, and software
// data protection remains ENABLED after the erase completes -- this
// operation does not lock or unlock SDP as a side effect of erasing.
//
// This is deliberately NOT the datasheet's HARDWARE Chip Erase mode
// (AT28C256 DS20006386B Table 6-1), which drives 12V onto the OE pin --
// DIP28_28C256 pin 22 is OE. This handler energises no programming rail of
// any kind. The sibling hardware-erase path already exists in this tree,
// at flash_5v_page.cpp lines 196-231; it is a different file, a different
// function, and a different electrical mechanism, and nothing in this body
// resembles it.
//
// This operation is prefixed with an SDP-disable sequence, by reusing
// eeprom28c_sdp_unlock_execute(handle) verbatim, even though AN 0544B is
// silent on whether the six-byte erase code is decoded on a protected part.
// The asymmetry: if it is not decoded while protected, the failure is a
// phantom erase that reports OK having erased nothing -- and on this family
// SDP state is unreadable, so no oracle could ever catch that phantom erase
// after the fact. The cost of disabling SDP first, on an already-unprotected
// part, is six harmless extra bus writes and one t_WC wait. Silence is not
// permission when the failure mode this way is invisible.
//
// This erase is device-global by construction -- the AN 0544B sequence
// erases the whole part -- and it ignores any sector address; no post-erase
// blank check is wired (`erase -b` stays a documented no-op here, `blank`
// remains its own independent step).
//
// The six inline writes below are transcribed from flash_utils.h's
// FLASH_ERASE table (lines 34-41) rather than referencing it, at 0 B RAM
// cost: the header is byte-frozen, and a reference would duplicate the table
// into this translation unit at the same RAM cost anyway. That transcription
// is pinned against the tree, not against this comment's prose, by a native
// full-stream equality case comparing this operation's emitted stream,
// positionally, against a composite reference built from
// SDP_FIXED_DIP28_28C256 and FLASH_ERASE.
//
// No native test can prove the t_EC wall-clock wait below: the native host
// stubs leave delay() unstubbed and record no time, so the only available
// proof that the wait exists is structural (a source-level assertion that
// the call is present), never a timing measurement.
static void eeprom28c_erase_execute(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHIP_ERASE);
    eeprom28c_sdp_unlock_execute(handle);
    // eeprom28c_wait_for_sdp_completion (inside the prefix above) ends in
    // reads through handle->firestarter_get_data, which leaves the data bus
    // configured as an input. Re-arm it for output before the first erase
    // write below, or every erase byte is silently dropped.
    rurp_set_data_output();
    handle->firestarter_set_data(handle, 0x5555, 0xAA);
    handle->firestarter_set_data(handle, 0x2AAA, 0x55);
    handle->firestarter_set_data(handle, 0x5555, 0x80);
    handle->firestarter_set_data(handle, 0x5555, 0xAA);
    handle->firestarter_set_data(handle, 0x2AAA, 0x55);
    handle->firestarter_set_data(handle, 0x5555, 0x10);
    delay(AT28C_TEC_MAX_MS);
}

void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip identity via A9-12V BEFORE SDP-disable: failing fast on
    // identity leaves the chip write-protected on mismatch.
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    if (!is_flag_set(FLAG_SKIP_SDP_UNLOCK)) {
        // Sequence length hoisted to ONE expression: the t_BLC runtime
        // budget check derives from this exact local, so there is exactly
        // one length expression in this function -- a second copy would be
        // a silent second source of truth.
        size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);

        // LOAD-BEARING: the report pair emitted below is UNCONDITIONAL --
        // via the bare LOG_ID / LOG_ID_U32 macros on an INFO-band id, NOT
        // the FLAG_VERBOSE-gated LOG_INFO_ID* family. Gating behind
        // FLAG_VERBOSE would leave a default `firestarter write at28c256`
        // silent, which is the exact defect this reporting exists to
        // remove. A released host that has never seen these ids degrades
        // gracefully: codec.py logs "Unknown message ID 0x.. -- catalog out
        // of date?" and drops the frame -- no crash, no garbled render.
        //
        // Disable SDP (Software Data Protection) before writing, through
        // handle->firestarter_set_data (i.e. memory_set_data), which applies
        // the full remap via mem_util_remap_address_bus and rewrites
        // CONTROL_REGISTER on every address change -- closing both the
        // /WE-inhibit defect measured for 66 of the 84 0x0D chips
        // (flash_util_byte_flipping's fu_flash_fast_address bypasses
        // handle->bus_config entirely) and, for the 18 chips at 64 KB and
        // above on DIP32_28C512_EEPROM, the A16-A18 upper-address staleness
        // gap -- both close as one by-product of this single routing change,
        // not as two separate fixes. handle->pulse_delay is already 0 for
        // this protocol (see configure_eeprom28c above).
        //
        // The report pair, the micros() bracket and the t_BLC budget check
        // all live in the shared eeprom28c_emit_sdp_sequence_timed helper
        // above, so the standalone eeprom28c_sdp_unlock_execute /
        // _lock_execute ops share this exact shape rather than duplicating
        // it -- see that helper's comment for the full bracket/budget
        // rationale.
        eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE, sdp_seq_len, MSG_INFO_SDP_UNLOCK,
                                           MSG_INFO_SDP_UNLOCK_DONE_US);

        // Wait for the SDP-disable internal write cycle to complete. There
        // is no valid form of a guarded read-back at address 0x5555
        // comparing against terminal byte 0x20 -- see
        // eeprom28c_wait_for_sdp_completion's comment above for why -- so
        // none is done here. This wait never aborts write-init and never
        // touches response_code.
        eeprom28c_wait_for_sdp_completion(handle);
    } else {
        // The skip path replaces the ENTIRE unlock block above -- report
        // pair, micros() bracket, budget check, AND the completion wait --
        // with exactly one unconditional WARN. There is no internal write
        // cycle to wait for when no command sequence was emitted, so
        // waiting AT28C_TWC_MAX_MS and polling would be pure latency plus
        // two recorded read strobes the native absence assertion would then
        // have to explain away. WARN, not INFO: on an SDP-protected part a
        // skipped unlock means the write will not land, so the user must be
        // told loudly -- but on an unprotected part the skip is harmless, so
        // the severity lives in the log line's band alone, never fabricated
        // into an operation-level response_code (no write here, enforced
        // permanently by
        // test_case8_completion_poll_preserves_prior_severity). The
        // MSG_INFO_SKIPPING_ERASE INFO shape at flash_5v_page.cpp:71 was
        // considered and rejected: `write -b` silently skipping erase is a
        // footgun this project has already had to fix once -- it skipped
        // erase entirely and still reported success -- and an INFO-severity
        // skip of a write-protection removal would repeat that exact
        // mistake. FLAG_SKIP_SDP_UNLOCK is 0x100 on the wire, parsed
        // unchanged by get_flags's extract_long (json_parser.c).
        LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED);
    }
    // No pre-write blank check on this protocol. On 0x0D the silicon
    // auto-erases per page during the write itself, and
    // eeprom28c_verify_page_readback already read-back-verifies every page,
    // so a pre-write blank check was never a safety net here -- it was a
    // false precondition that made a non-blank AT28C part un-writable
    // without a flag. FLAG_SKIP_BLANK_CHECK is consequently UNREAD on this
    // protocol; do not restore this conditional on the grounds that the bit
    // looks orphaned. `blank` remains available as its own step through the
    // untouched CMD_BLANK_CHECK arm above. No FLAG_CAN_ERASE-gated
    // erase-on-write block is added here in its place either: erase is a
    // standalone step on this protocol, and both sibling handlers'
    // erase-on-write blocks (flash_5v_page.cpp, flash_nor_unlock.cpp) are a
    // pattern to recognise, not to copy.
}

// Resolve the validated flush mask from a delivered page-size. Returns
// `requested - 1` when `requested` is a power of two in
// [1, AT28C_PAGE_SIZE_MAX], and AT28C_PAGE_SIZE_FALLBACK - 1 otherwise.
//
// Zero MUST be rejected before the subtraction -- the check below tests
// `requested == 0` first, deliberately, because the power-of-two test alone
// (`(requested & (requested - 1)) == 0`) admits 0. `0 - 1` on an unsigned
// type wraps to an all-ones mask, which would flush almost never -- the
// dangerous direction, since a page load that never flushes never gets
// read-back-verified until the very last byte.
//
// The fallback is silent by design: a new message ID would cost PROGMEM
// against a leonardo budget with 0 bytes of headroom, to report a condition
// only our own host could cause -- the compensating control is the
// exhaustive host-side invariant (tests/test_page_size_invariants.py) that
// every emitted page_size is a power of two in range, for every one of the
// 746 chips in the generated database. This function's return value is only
// ever ANDed with an address below, never used to index memory, so the
// failure mode of a wrong `requested` is wrong flush granularity, never a
// buffer overrun.
static uint32_t eeprom28c_page_mask(uint16_t requested) {
    if (requested == 0) {
        return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
    }
    if (requested <= AT28C_PAGE_SIZE_MAX && (requested & (requested - 1)) == 0) {
        return (uint32_t)requested - 1;
    }
    return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
}

void eeprom28c_write_execute(firestarter_handle_t* handle) {
    // The validated flush mask, resolved ONCE here, above the per-byte loop
    // -- never per byte, and never a runtime `%` by a variable divisor
    // (which would pull __udivmodsi4 into a build with zero flash
    // headroom). Three measured reasons this site was chosen over
    // eeprom28c_write_init:
    //   1. `--policy merge05` requires ram_used EXACTLY unchanged; a second
    //      stored field (on the handle or as a file-scope static) would
    //      cost RAM for no behavioural gain.
    //   2. eeprom28c_write_init has an early `return` on a chip-ID
    //      mismatch, so a mask resolved after it would be only
    //      conditionally initialised.
    //   3. Every existing native case in this suite calls
    //      configure_memory(&h) then h.firestarter_operation_main(&h) and
    //      NEVER firestarter_operation_init -- a mask resolved in
    //      write_init would leave every test_fix06_* case at mask 0
    //      (flushes every byte), silently changing
    //      test_fix06_page_boundary_window_readback's two-window geometry.
    //      write_execute's top is reached by every existing case and every
    //      new one.
    const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);
    // Window-start index into handle->data_buffer for
    // eeprom28c_verify_page_readback below. The read-back covers ONLY the
    // bytes of the CURRENT flush window, not the whole physical page --
    // bytes a prior chunk wrote are no longer in handle->data_buffer
    // (re-reading them would either fabricate an expected value or require
    // re-deriving data the handle does not hold). Each chunk's own flush
    // already read-back-verified its own bytes, so coverage of every byte
    // THIS operation wrote is complete without it. Invariant:
    // window_start <= i < handle->data_size by construction -- i is the
    // for-loop variable below, never derived from a wire field directly, so
    // no index here can exceed data_size or DATA_BUFFER_SIZE.
    uint32_t window_start = 0;
    // This per-byte set_data loop runs with handle->pulse_delay = 0 and no
    // inter-byte wait, under the IDENTICAL AT28C_TBLC_MAX_US constraint as
    // the SDP-disable command sequence (eeprom28c_emit_command_sequence,
    // above) -- both are byte-load sequences bounded by the same datasheet
    // t_BLC maximum, and that is the shared physical exposure named there.
    //
    // gh#11's REAL SHAPE, restated in this function's own words: a
    // completion-and-data-landed CONFLATION bug -- a whole-byte equality
    // compare that passed spuriously whenever the old byte already equalled
    // the new one. NOT a sampling-rate or polling-frequency bug. It is now
    // split into eeprom28c_wait_for_page_write (completion only) and
    // eeprom28c_verify_page_readback (data-landed only), below. Any future
    // work revisiting gh#11 on real silicon should look at that conflation,
    // not at this loop's sampling rate.
    //
    // WHAT THE TRACKED NUMBER IS AND IS NOT: page_load_worst_us (below) is
    // the host-side interval between consecutive firestarter_set_data calls,
    // as measured by the MCU's OWN micros(). It is a measurement of the MCU
    // driving its own latches. It says NOTHING about whether an AT28C die
    // accepted any given byte, and NOTHING about whether t_BLC is met AS
    // ACCEPTED BY THE DIE -- and that last item is not provable at all
    // without an AT28C part on the bench.
    //
    // WHY THERE IS NO CHECK HERE: a runtime budget comparison in this hot
    // per-byte path is explicitly declined. The
    // `if (page_load_interval_us > page_load_worst_us)` compare just below
    // is a MAX-TRACKING compare, not a budget check -- there is no
    // AT28C_TBLC_MAX_US comparison and no LOG_WARN_* call anywhere in this
    // function. A per-byte compare against the budget would cost flash and
    // cycles for a surface nothing requires, and the flash delta matters:
    // headroom on this target is measured in hundreds of bytes.
    //
    // WHY THIS LOOP IS MEASURED AT ALL: on a real Leonardo the unlock
    // emitter measured 572 us against a 600 us budget -- about 95 us per
    // byte against a 100 us per-byte datasheet maximum, only 4.7% headroom
    // -- against an earlier premise that the check would never fire. This
    // loop runs under the identical per-byte constraint, so it is measured
    // rather than merely cited.
    uint32_t page_load_worst_us = 0;
    uint32_t page_load_previous_us = micros();
    // Single-exit structure: the two loop exits below set this flag and
    // `break` rather than returning early. The write still stops at the same
    // byte, and eeprom28c_wait_for_page_write /
    // eeprom28c_verify_page_readback still emit their own errors and set
    // their own response_code before returning false -- this structure adds
    // no error and suppresses none. It exists so the worst-interval report
    // below is reachable on BOTH exits: with an EMPTY SOCKET the very first
    // page's write poll fails, so a report placed only at the loop's normal
    // exit would emit nothing at all -- and an empty socket is both a
    // routine bench condition and exactly the condition in which gh#11's
    // symptom appears. On an aborting write the reported value covers only
    // the bytes loaded before the abort, which is a real and useful number
    // but is NOT a full-write figure.
    bool page_load_aborted = false;
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        uint32_t page_load_now_us = micros();
        uint32_t page_load_interval_us = (uint32_t)(page_load_now_us - page_load_previous_us);
        if (page_load_interval_us > page_load_worst_us) {
            page_load_worst_us = page_load_interval_us;
        }
        page_load_previous_us = page_load_now_us;

        bool page_end = ((address + 1) & page_mask) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            // Completion and data-landed proof are two functions with one
            // job each. eeprom28c_wait_for_page_write answers ONLY "is the
            // internal write cycle done" (DQ7-complement poll);
            // eeprom28c_verify_page_readback answers ONLY "did the data
            // land" (per-byte read-back). Conflating both into a single
            // whole-byte equality compare is the defect this split
            // removes.
            if (!eeprom28c_wait_for_page_write(handle, address, data)) {
                page_load_aborted = true;
                break;
            }
            if (!eeprom28c_verify_page_readback(handle, window_start, i)) {
                page_load_aborted = true;
                break;
            }
            window_start = i + 1;
        }
    }
    (void)page_load_aborted;  // recorded for reader clarity only; both exits report identically (D-16)
    LOG_ID_U32(MSG_INFO_PAGE_LOAD_WORST_US, page_load_worst_us);
}

// Completion detection ONLY -- a DQ7-COMPLEMENT poll, the canonical AT28C
// completion protocol (see AT28C_DQ7_MASK above). This function draws NO
// conclusion about whether the byte's VALUE landed correctly -- that is
// eeprom28c_verify_page_readback's job, below. It compares only the DQ7 bit,
// never the whole byte: a whole-byte equality compare is the conflation this
// split removes (see AT28C_DQ7_MASK's comment for why that is exactly
// gh#11's shape).
//
// Double-read idiom (flash_util_verify_operation, flash_utils.cpp:37-39,
// READ-ONLY ANALOG, byte-frozen): the DQ7 match must hold on TWO CONSECUTIVE
// reads before the poll returns done, so a single transient sample (a read
// landing mid-toggle) cannot end the poll early.
//
// Every read goes through handle->firestarter_get_data (memory_get_data) --
// never a direct rurp_* read, never fu_flash_data_poll() (flash_utils.cpp,
// byte-frozen): that helper emits four recorded strobes per read, which
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

// Data-landed proof ONLY -- a per-byte read-back over the CURRENT flush
// window (handle->data_buffer[first_index..last_index], inclusive), reusing
// memory_verify_execute's verify-mismatch payload order (memory.cpp): the
// five bytes expected, observed, addr>>16, addr>>8, addr, where addr is the
// FAILING address. A poll that bare-returns mid-buffer carrying only the
// poll address gives no per-byte attribution; this one does.
//
// This read-back is ALWAYS ON, with NO opt-out. Firmware owns the truth
// about whether its own page write landed; reporting success it cannot
// substantiate is the defect this read-back corrects. An opt-out would need
// a new FLAG_* value landing in lockstep across firestarter.h and the host's
// constants.py -- a cross-repo change, not a local one, and
// firmware-before-host forbids emitting it early. Redundancy with the host's
// own verify pass is ACCEPTED: the host's pass proves the image landed; this
// one proves THIS PAGE'S write cycle landed, and only the second can
// attribute a failure to a page.
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
