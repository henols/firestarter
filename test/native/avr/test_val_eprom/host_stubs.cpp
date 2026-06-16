/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 71 Plan 04 — host stub TU for the test_val_eprom Tier-1 suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_RECORD_BUS: activate the recording buffer so the test can
 *     observe all rurp_write_to_register calls and assert VPP-enable CTL bits.
 *   - HOST_STUBS_CUSTOM_HW_REVISION: override hardware revision to return 1
 *     (non-REV0) so eprom_check_vpp does NOT take the REVISION_0 early-return
 *     path — the VPP write that the positive test asserts WILL fire.
 *
 * PITFALL 1 (from 71-PATTERNS.md): HOST_STUBS_RECORD_BUS MUST be defined
 * BEFORE #include of host_stubs_common.inc — the guard reads at include time.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate recording bus stub (opt-IN). */
#define HOST_STUBS_RECORD_BUS

/* Opt out of default hw-revision stub so we can return non-REVISION_0.
 * Without this, rurp_get_hardware_revision() returns 0 = REVISION_0 and
 * eprom_check_vpp takes the early-return path, never writing VPP bits. */
#define HOST_STUBS_CUSTOM_HW_REVISION

#include "../_shared/host_stubs_common.inc"

/* Suite-local hw-revision mock: always return 1 (non-REV0) so the VPP write
 * path is reachable in eprom_check_vpp. */
#ifdef HARDWARE_REVISION
static uint8_t s_mock_hw_rev = 1;
extern "C" void set_mock_hw_rev_eprom(uint8_t r) { s_mock_hw_rev = r; }
extern "C" uint8_t rurp_get_hardware_revision() { return s_mock_hw_rev; }
#endif
