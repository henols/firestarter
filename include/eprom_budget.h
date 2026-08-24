/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * The per-block worst-case write-time budget arithmetic. This header declares
 * three pure functions; the arithmetic itself lives in
 * src/proms/eprom_budget.cpp, this header's .cpp analog.
 *
 * (a) This header deliberately does NOT include the platform PROGMEM
 *     compatibility shim (include/rurp_platform_compat.h): it declares no
 *     PROGMEM object and no struct, so it needs neither that shim nor any
 *     pgm_read_* macro. The one PROGMEM-backed table this arithmetic reads
 *     from (eprom_params_t, via eprom_params_for) is entirely the .cpp's
 *     concern.
 * (b) This header deliberately does NOT include, and nothing it includes
 *     may include, any Arduino framework header (restated from
 *     include/eprom_params.h's own header comment): a
 *     translation unit that pairs that framework header with the platform
 *     PROGMEM shim emits 14 macro-redefinition warnings, and the native
 *     build's warning watermark sits at exactly 1166 with zero headroom --
 *     so this dependency stays out end to end. This header includes only
 *     <stdint.h>.
 *
 * The per-byte bound is NOT min(max_pulses x pulse, energy_cap_us), the
 * form a naive reading suggests. That form is WRONG -- the shipped
 * per-byte loop (src/proms/eprom.cpp's
 * inner `for (;;)`) does `accumulated += org_delay` BEFORE testing
 * `accumulated >= energy_cap_us`, so the last pulse can overshoot the cap
 * by up to `pulse_us - 1`. The functions below implement the corrected
 * form; see each declaration for the exact rule it carries.
 */
#ifndef __EPROM_BUDGET_H__
#define __EPROM_BUDGET_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Worst-case pulse COUNT for one byte, corrected per BF-3.
 *
 * Semantic rules a caller must not get wrong:
 * (a) energy_cap_us == 0 means UNCAPPED, not "cap at zero" -- the same
 *     reading include/eprom_params.h states for the column, and the same
 *     rule src/proms/eprom.cpp's pre-flight refusal guards with
 *     `energy_cap_us > 0`. An unguarded min() would clamp every 0x07/0x08
 *     pulse to zero, since both of those rows ship energy_cap_us == 0.
 * (b) The pulse count is min(max_pulses, ceil(energy_cap_us / pulse_us)),
 *     NOT min(max_pulses * pulse_us, energy_cap_us) / pulse_us implied by
 *     a naive reading -- the shipped loop increments the
 *     accumulator and only THEN tests it, so the true pulse count can
 *     exceed a naive energy_cap_us / pulse_us division. Example: at
 *     pulse_us = 49999 against energy_cap_us = 50000, a naive
 *     min(max_pulses * pulse_us, energy_cap_us) reading implies the per-byte
 *     bound is 50000 us (one pulse); the real loop needs a SECOND pulse
 *     before the accumulated total (99998 us) reaches the cap -- a 2x
 *     under-estimate on a host-legal, firmware-accepted `--pulse-us` value
 *     (BF-3).
 * (c) pulse_us == 0 returns max_pulses, so this function never divides by
 *     zero. This is a GUARD, not the live path: configure_eprom's own
 *     pulse-fallback switch has already resolved a zero pulse_delay by the
 *     time any ack is packed (verified chain: parse_json calls
 *     configure_memory, and init_programmer_framed calls parse_json and
 *     only emits the ack afterwards).
 */
uint32_t eprom_worst_pulses(uint8_t max_pulses, uint32_t pulse_us, uint32_t energy_cap_us);

/*
 * Worst-case per-byte program TIME in microseconds: the pulse count above,
 * times the pulse width, plus the shipped overprogram duration for that
 * same pulse count.
 *
 * This function and the one above take the column values EXPLICITLY --
 * max_pulses, energy_cap_us, overprogram_factor, overprogram_cap_us --
 * rather than a protocol id, and that is deliberate and load-bearing,
 * matching the voice include/eprom.h already uses to justify exposing the
 * shipped overprogram-duration function rather than keeping it file-static:
 * overprogram_factor is 0 on every one of the three shipped rows
 * (0x07/0x08/0x0B), so an API keyed ONLY on protocol id would make the
 * overprogram term structurally unreachable by any native case driven off
 * shipped data, and BF-3's second correction below would be unprovable.
 *
 * The overprogram term is produced by CALLING the shipped
 * eprom_overprogram_us (declared in eprom.h) with the pulse count this
 * function just derived -- never by restating that function's formula.
 * Restating it as a literal `3 * overprogram_factor * pulse_us` (the
 * reading include/eprom_params.h's own column comment suggests) would
 * under-estimate 8.3x for the first future row
 * that sets a non-zero factor, because `3` already IS the factor in the
 * shipped function's contract and its `pulse_count` parameter is not `3`
 * again.
 */
uint32_t eprom_per_byte_budget_us(uint8_t max_pulses, uint32_t pulse_us, uint32_t energy_cap_us,
                                   uint8_t overprogram_factor, uint32_t overprogram_cap_us);

/*
 * Advertised per-block write-time budget, in whole SECONDS, for one
 * DATA_BUFFER_SIZE-class block -- already PADDED. A host-side
 * reader cannot see the padding rule from the wire, so it is recorded here
 * in prose:
 *
 *   padded_s = ceil(raw_pulse_only_us / 1e6) * 2 + 2
 *
 * "Twice the ceil-rounded pulse-only worst case, plus two seconds." A
 * MULTIPLIER, not an additive constant, because the per-pulse fixed
 * overhead scales with pulse COUNT, not with block size alone: at 0x0B /
 * --pulse-us 200 the per-byte loop runs 250 pulses x 1024 bytes = 256 000
 * iterations, and an [ASSUMED], NOT measured, ~20-60 us per-pulse
 * overhead adds roughly 15 s on top of a 51.2 s
 * pulse-only budget -- about 30%. A flat +N seconds could never absorb
 * that at every pulse width.
 *
 * What raw_pulse_only_us counts: pulse widths only
 * (eprom_per_byte_budget_us above), times the block's byte count. What the
 * x2+2 padding absorbs, that the raw figure never counts: the
 * once-per-block VPE settle (500 ms), the per-pulse pre-pulse settle, the
 * verify read strobe, the shift-register writes behind every address
 * change, the 0x07/0x08 final full-block verify pass, and the serial
 * transport cost of one chunk (~41 ms per 1024 B at 250000 baud). The "+2"
 * makes a one-second floor automatic, so no separate floor clamp is needed
 * anywhere in this budget.
 *
 * Returned-value contract: returns 0 when the protocol has no
 * eprom_params row (eprom_params_for(protocol) == NULL) -- a non-EPROM
 * protocol. 0 means "advertise nothing", never "no time needed": the
 * host's own plausibility clamp then leaves its corresponding attribute
 * None, and the host's own fallback applies -- the correct behaviour for a
 * family whose block time this table cannot bound.
 */
uint16_t eprom_block_budget_s(uint32_t protocol, uint32_t pulse_us, uint32_t block_bytes);

#ifdef __cplusplus
}
#endif

#endif /* __EPROM_BUDGET_H__ */
