/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 12 Wave 1 — host stub TU for the test_flash_intel_vpp suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions (these REPLACE the shared defaults — opt out
 * via HOST_STUBS_CUSTOM_* before including the shared file):
 *   - rurp_read_voltage_mv() is mockable via set_mock_vpp_mv() so the
 *     SAF-04 VPP-validation test can inject 12V vs out-of-spec readings.
 *   - rurp_get_hardware_revision() is mockable via set_mock_hw_rev() so
 *     the test can simulate REV0 vs non-REV0 board behaviour.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Opt out of the shared defaults for the two mockable symbols. The shared
 * include conditions its `rurp_read_voltage_mv` and `rurp_get_hardware_revision`
 * definitions on the absence of these macros. */
#define HOST_STUBS_CUSTOM_VOLTAGE_MV
#define HOST_STUBS_CUSTOM_HW_REVISION

#include "../_shared/host_stubs_common.inc"

/* Suite-local mockable VPP voltage — TU-private state; test TU calls
 * set_mock_vpp_mv() to inject a value before calling into flash_intel_write_init. */
static uint16_t s_mock_vpp_mv = 0;
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }

#ifdef HARDWARE_REVISION
/* Suite-local mockable hardware revision — TU-private state; test TU calls
 * set_mock_hw_rev() to simulate REV0 vs non-REV0 boards. */
static uint8_t s_mock_hw_rev = 1;
extern "C" void set_mock_hw_rev(uint8_t r) { s_mock_hw_rev = r; }
extern "C" uint8_t rurp_get_hardware_revision() { return s_mock_hw_rev; }
#endif
