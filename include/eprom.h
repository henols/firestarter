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

#ifdef __cplusplus
}
#endif
#endif // __EPROM_H__