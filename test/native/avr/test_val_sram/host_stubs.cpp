/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 71 Plan 04 — host stub TU for the test_val_sram Tier-1 suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_RECORD_BUS: activate the recording buffer so the test can
 *     observe all rurp_write_to_register calls and assert the zero-write
 *     no-op baseline for the SRAM handler.
 *
 * PITFALL 1 (from 71-PATTERNS.md): HOST_STUBS_RECORD_BUS MUST be defined
 * BEFORE #include of host_stubs_common.inc.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate recording bus stub (opt-IN). No other overrides needed. */
#define HOST_STUBS_RECORD_BUS

#include "../_shared/host_stubs_common.inc"
