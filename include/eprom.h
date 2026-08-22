/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __EPROM_H__
#define __EPROM_H__

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    void configure_eprom(firestarter_handle_t* handle);

    /*
     * Phase 141 Plan 04 (LOOP-03, D-08) -- pure overprogram-duration
     * arithmetic. Exposed here (not file-static in eprom.cpp) because D-08
     * requires direct native testing: overprogram_factor is 0 on all three
     * shipped eprom_params rows (0x07/0x08/0x0B), so the per-byte write
     * loop can never reach this path with today's data, and a pure
     * function is the only possible oracle for LOOP-03's correctness.
     *
     * The product is computed entirely in uint32_t
     * ((uint32_t)factor * pulse_count * pulse_us) -- the worst named case
     * (factor=3, pulse_count=25, pulse_us=65535) is 4,915,125, which fits
     * uint32_t (max 4,294,967,295) but overflows any uint16_t
     * intermediate. cap_us == 0 yields 0 (0 means "no clamp is
     * configured" -- eprom_params.h's fail-safe reading; "0 means
     * uncapped" would let the worst case above emit a multi-second VPE
     * pulse).
     */
    uint32_t eprom_overprogram_us(uint8_t pulse_count, uint32_t pulse_us, uint8_t factor, uint32_t cap_us);

    /*
     * Phase 142 Plan 04 (D-05, D-06, Q4) -- resolves which EPROM
     * high-voltage route (direct-VPE vs. drop-resistor) to assert for the
     * current handle, driven by the eprom_params table's vpp_path column,
     * with FLAG_VPE_AS_VPP forcing the direct-VPE path on top of whatever
     * the table says. Both eprom_write_execute and eprom_check_vpp call
     * this same function (VPP-03), replacing the two byte-identical
     * hand-rolled forks eprom.cpp used to carry at what were :190 and :340.
     *
     * Exposed here (not file-static in eprom.cpp), matching the
     * eprom_overprogram_us precedent immediately above: a direct
     * (protocol, ctrl_flags) -> mask truth table is VPP-01's clearest
     * evidence, and it is the only way to exercise the fail-closed
     * NULL-row arm without a full drive -- a file-static resolver could
     * only ever be tested through its effects on the emitted strobe
     * stream.
     *
     * rurp_register_t is already reachable from this header through
     * firestarter.h (:11 above) -> rurp_shield.h -> rurp_types.h, so this
     * declaration adds no new include edge.
     */
    rurp_register_t eprom_hv_route_mask(firestarter_handle_t* handle);

    /*
     * Phase 143 Plan 05 (HOST-02, D-02/D-03) -- cadence for the intra-block
     * MSG_DATA_PROGRESS (0xE0) emission inside eprom.cpp's per-byte program
     * loop, which runs on leonardo and native only (compiled out, variable
     * and all, on uno/uno328pb -- see that emission's own comment in
     * eprom.cpp for the BF-2 rationale). Named here, not as a file-local
     * #define in eprom.cpp (a #define costs 0 B until referenced), so the
     * native cadence cases in test_loop_eprom_v131.cpp can reference it by
     * name instead of duplicating the number.
     *
     * 1000 ms is chosen so that even against a host that somehow kept the
     * OLD 10 s response-window timeout (HOST-01 raises it; this constant's
     * value is independent of that raise), the window is still fed with
     * 10x margin. At the modal 0x07 pulse width (100 us, max_pulses 25,
     * energy_cap_us 0 == uncapped) a full 1024-byte block worst-cases at
     * ~2.6 s (1024 * 25 * 100us), so a 1 s interval yields about 2 frames
     * per block -- visible bar movement at negligible wire cost. At
     * --pulse-us 65535 (the same uncapped row's worst case, and the CLI's
     * own pulse ceiling) a block takes about 1678 s (1024 * 25 * 65535us),
     * giving about 1678 frames of 10 payload bytes each (1 id + 8 params +
     * 1 crc, per _firestarter_emit_frame's own len_u16 accounting) --
     * roughly 17 kB over ~28 minutes, irrelevant at 250000 baud. A larger
     * interval such as 5 s would make the progress bar feel dead on an
     * ordinary write without saving anything that matters.
     */
    #define EPROM_PROGRESS_EMIT_INTERVAL_MS 1000

    /*
     * Debug session w27c512-program-fail-byte0 (Phase 145 Gate 2) -- the
     * settle either side of the program-voltage route assert that wraps
     * every program pulse in eprom.cpp's per-byte loop.
     *
     * WHY THE WRAP EXISTS AT ALL. Phase 141 rewrote eprom_write_execute as
     * a per-byte pulse-to-verify loop and deleted program_mismatched_bytes()
     * "outright" (141-PATTERNS.md:158). That function was the ONLY place the
     * write path ever asserted CTRL_VPE_ENABLE -- it wrapped each program
     * pass in set_control_register(CTRL_VPE_ENABLE, 1) / delay(10) / ... /
     * set_control_register(CTRL_VPE_ENABLE, 0). The replacement loop calls
     * firestarter_set_data() bare, and memory_set_data() (memory.cpp) writes
     * no control register of its own, so from Phase 141 until this fix every
     * CE program strobe on 0x07/0x08/0x0B was emitted with the 12 V rail
     * generated but never switched onto the socket. The repo's own two
     * empirical golden traces show it directly: the pre-v1.31 capture latches
     * 0x85/0x95 into CONTROL_REGISTER during the program pass on 0x07 (bit
     * 0x04 set), the post-v1.31 capture latches only 0x81/0x91.
     *
     * WHY PER PULSE AND NOT ONCE PER BLOCK. The W27C512 datasheet's TABLE OF
     * OPERATING MODES makes both halves mandatory: Program is entered with
     * CE = VIL and OE/VPP = VPP (12 V), while Program Verify requires OE/VPP
     * LOW. On this family the program voltage and the output-enable control
     * share one pin, so the route MUST come down before the loop's verify
     * read and go back up for the next pulse. A once-per-block assert (which
     * memory.cpp's unconditional preserve mask would happily carry) would
     * leave the part in Output Disable for every verify and the loop would
     * never converge. The old code got its amortisation from batching a
     * whole pass of pulses before one verify pass; a per-byte loop cannot.
     *
     * VALUES -- DATASHEET FLOOR, THEN MEASURED. TOES ("OE/VPP Setup Time")
     * is 2.0 us MIN and TVS ("OE/VPP Valid after CE High") is 2.0 us MIN,
     * both from the W27C512 AC PROGRAMMING/ERASE CHARACTERISTICS table;
     * OE/VPP rise time (TPRT) is 50 ns MIN. Those are the CHIP's floors. The
     * values below are 500x and 50x them, and the extra margin is not
     * decoration: the RURP shield's own VPE switch rise time is a BOARD
     * property that no measurement in this project has ever characterised,
     * and this session could not characterise it either (no DMM available).
     *
     * The pair was therefore chosen on the bench, not from the datasheet.
     * At the first values tried, 100 us / 10 us, the loop programmed
     * correctly -- write time held at ~40 s per 64 KiB, which is the ~1
     * pulse per byte figure, so the pulses were plainly effective -- but 1
     * of 3 full 64 KiB cycles failed its final full-array verify on a SINGLE
     * byte (0x85 read back as 0xc5 at 0x007acf: bit 6 took enough charge to
     * pass the per-pulse verify and not enough to hold). At 1000 us / 100 us
     * that did not recur in 11 consecutive 64 KiB cycles across three
     * different images -- 719 424 programmed bytes, zero margin failures,
     * every cycle byte-exact against an independent read-back. Stated
     * honestly: 11/11 against 2/3 is suggestive, not proof (p ~ 0.025 under
     * the null of an unchanged per-byte failure rate), and the residual
     * could equally have been a marginal cell or a program-window VPP droop
     * that this session had no instrument to see. The larger value is the
     * conservative choice, and it is cheap in the only currency that matters
     * here.
     *
     * The COST, so nobody has to re-measure it: ~110 s per 64 KiB write, up
     * from ~40 s at 100 us. That is well inside budget -- a 1024-byte
     * Leonardo block spends about 1.13 s in these settles against the 8 s
     * this protocol's own CAP-03 advertisement asks the host to wait
     * (eprom_budget.h). This is also the ceiling on how far these values can
     * grow: the deleted code's delay(10) was paid once per block-PASS, so it
     * could be arbitrary, but at per-pulse granularity 10 ms would cost
     * 1024 x 10 ms = 10.2 s per block and convert a working write into a
     * host transport timeout. Anything above ~7 ms is unsafe for that reason
     * alone, quite apart from the AVR delayMicroseconds ceiling of 16383 us
     * that tests/test_write_path_source_contract_v131.py range-checks.
     *
     * SELF-CORRECTING, WITHIN LIMITS: a mild under-settle does not corrupt,
     * it only wastes a pulse -- the loop re-pulses up to max_pulses. Two
     * limits on that comfort, both observed above. An under-settle bad
     * enough to make every pulse ineffective reappears as
     * MSG_ERR_MAX_PULSES, the exact symptom this fix was written for. And an
     * under-settle that is merely MARGINAL is not self-correcting at all: it
     * converges the per-pulse verify on a weakly programmed cell and only
     * shows up later, as MSG_ERR_VERIFY from the full-array pass. A future
     * bench failure of EITHER shape must be re-discriminated by raising
     * these values before anyone concludes the part is worn.
     */
    #define EPROM_VPP_SETUP_US 1000
    #define EPROM_VPP_HOLD_US  100

    /*
     * EPROM_ERASE_PULSE_US -- the CE pulse width eprom_internal_erase spends
     * with OE/VPP and A9 both at VPE. Debug session
     * w27c512-devtest-all-bad.
     *
     * WHY THIS CONSTANT EXISTS. Before it, eprom_internal_erase spent
     * `handle->pulse_delay` here -- the per-BYTE PROGRAM pulse width, which
     * arrives from the host as the database's `pulse_duration_us` (100 for
     * W27C512, 50 for the SST 27SF/27VF rows, 10 for SST 37VF). That value
     * describes a completely different operation. The Winbond W27C512
     * datasheet specifies the CE erase pulse width T_PWE as 95 ms min /
     * 100 ms typ / 105 ms max, so the shipped firmware was emitting an
     * erase pulse roughly 950x below the datasheet MINIMUM and the part only
     * ever partially erased. Because CMD_ERASE installs mem_util_blank_check
     * as its END phase and eprom_write_init runs erase-then-blank-check,
     * that ONE partial erase reported as FOUR failures from `dev test`
     * (write, verify, erase, blank-check all BAD) on a chip whose database
     * row, pinout, VPP, chip-ID and program pulse were all correct.
     *
     * WHY 100 ms AND NOT MORE. T_PWE has a datasheet MAXIMUM, not just a
     * minimum: over-erasing a flotox cell drives it toward depletion mode.
     * "Raise it for margin" is the wrong instinct here. 100 ms is the
     * typical, centred inside 95..105 ms, and
     * test_vpp_eprom_v131.cpp::test_erase_ce_pulse_width_is_the_datasheet_
     * erase_pulse_not_the_program_pulse asserts BOTH bounds against the
     * measured CE-low interval so a future widening fails there.
     *
     * WHY ONE CONSTANT FOR THE WHOLE FAMILY. eprom_internal_erase is the
     * only electrical erase the 0x07/0x08/0x0B EPROM family has, and it
     * implements one specific algorithm -- the Winbond 27C/27E one (A9 at
     * VPE, address 0, CE pulsed). 28 database rows reach it; the non-Winbond
     * ones (SST 27SF/27VF/37VF, LG/MX/PT 28Cxxx, M8720) were ALREADY being
     * driven with that algorithm, so pairing it with that algorithm's own
     * datasheet pulse width introduces no mismatch that was not there
     * before -- it removes one. A per-row erase width is deliberately NOT
     * introduced: minipro's infoic.xml carries no erase-duration attribute,
     * so the database generator could not source one without inventing a
     * field, and eprom_params.h's TABLE-02 forbids a pulse-width column.
     *
     * EXPRESSED IN MICROSECONDS, deliberately, so the value keeps going
     * through mem_util_delay_us's split helper: 100000 us is far above the
     * AVR delayMicroseconds() 16383 us ceiling, which is exactly the
     * hazard that helper exists to absorb.
     *
     * NOT VERIFIED ON SILICON. This value is datasheet-sourced and the
     * emitted pulse is unit-proven; no bench run has confirmed that it
     * erases a real W27C512.
     */
    #define EPROM_ERASE_PULSE_US 100000UL

#ifdef __cplusplus
}
#endif
#endif // __EPROM_H__
