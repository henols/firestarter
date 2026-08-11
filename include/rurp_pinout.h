/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * rurp_pinout.h — canonical CTRL_* / PIN_* / RES_* / JMP_* alias substrate
 * for the silkscreen-label → code-alias migration (Phase 33).
 *
 * This header introduces ONLY the new canonical declarations. Per D-06 no
 * backward-compat alias block is included (no `#define <old_name>
 * <new_name>` lines). The old #defines in rurp_shield.h:25-94 remain in
 * place during Wave 1 and serve all existing call-sites; Waves 2 and 3
 * migrate call-sites individually and Wave 3's final task atomically
 * deletes the rurp_shield.h:25-94 block.
 *
 * The #ifndef HARDWARE_REVISION / #else / #endif structure mirrors
 * rurp_shield.h:24-94 VERBATIM (Pitfalls 1 + 2):
 *   - Legacy branch: CTRL_ADDRESS_LINE_16 == CTRL_VPP_VPE_DROP_ENABLE
 *     (macro-alias-as-macro, NOT duplicate hex)
 *   - HARDWARE_REVISION branch: CTRL_VPP_VPE_DROP_ENABLE == 0x100
 *     (NOT 0x01 — value differs from legacy)
 */

#ifndef __RURP_PINOUT_H__
#define __RURP_PINOUT_H__

// NOTE: this header intentionally does NOT include <Arduino.h>. The `A2`/`A3`
// pin macros below expand to plain integer literals from Arduino's
// pins_arduino.h, which every consumer pulls via <Arduino.h> in their own TU.
// Including <Arduino.h> here would force C++ classes (String, etc.) through
// the extern-C wrappers of upstream headers like firestarter.h / flash_utils.h
// — a latent bracketing bug uncovered when rurp_shield.h started including
// rurp_pinout.h in Wave 3's D-06 atomic delete.
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// ---- Section 1: Arduino-pin assignments (PIN_*) ------------------------

#define PIN_VPP_VOLTAGE_ADC A2

#ifdef HARDWARE_REVISION
#define PIN_HW_REVISION_DETECT_ADC A3
#endif

// ---- Section 1b: ADC voltage-band thresholds (HARDWARE_REVISION-gated) -------
// Consumed by rurp_detect_hardware_revision() in rurp_hw_rev_utils.h.
// Phase 35 Wave 3 D-02 follow-through: thresholds UNCHANGED — Phase 35 Wave 3
// bench (2026-05-26) validated 0/15 reads in the [200, 220) guard gap across
// 3 shield revisions; the existing 20-count gap is empirically sufficient.
// SEMANTIC CHANGE post-Phase 35 Plan 01 INPUT high-Z fix: bands now characterize
// A3-net composition (R41-only-to-GND = low; external-pull-up-to-+5V = mid;
// floating = high), NOT R41 value alone. The internal pull-up R_top assumed in
// the Phase 34 band-math (INPUT_PULLUP at rurp_hw_rev_utils.h:43-pre-Plan-01)
// is disabled post-Plan 01 — R41 value no longer drives ADC variance.
// See .planning/v1.7-SHIELD-REVS.md §8 "Phase 35 ASCII correction" + §9 table
// + .planning/v1.7/bench-evidence-35.md §"Band-math semantics under Plan 01
// INPUT high-Z" for full analysis. v1.8 substrate seed: future Rev 2.4 PCB
// could add an external R_top to restore the original divider semantics.
// #define (NOT constexpr) per Phase 33 D-07 — preprocessor constants resolve
// at compile time and contribute 0 B to the .hex until referenced.
#ifdef HARDWARE_REVISION
#define ADC_BAND_R41_4K7_HIGH 200  // upper edge of low band (R41-only-to-GND; Rev 2.0/2.1/2.2 + Rev 2.3 stock post-Plan 01)
#define ADC_BAND_R41_10K_LOW  220  // lower edge of mid band (external pull-up active — operator-reworked boards); [200, 220) -> REVISION_UNKNOWN guard gap
#define ADC_BAND_R41_10K_HIGH 600  // upper edge of mid band; above -> high band / floating / no R41
#endif

// ---- Section 2: Control-register bits (CTRL_*) -------------------------
// Mirrors rurp_shield.h:24-53 VERBATIM under new names.

#ifndef HARDWARE_REVISION
#define CTRL_VPP_VPE_DROP_ENABLE      0x01
#define CTRL_ADDRESS_LINE_16          CTRL_VPP_VPE_DROP_ENABLE
#define CTRL_VPP_A9_ENABLE            0x02
#define CTRL_VPE_ENABLE               0x04
#define CTRL_VPP_P1_ENABLE            0x08
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40
#define CTRL_VPP_REGULATOR_ENABLE     0x80

#else
// HARDWARE_REVISION wide layout — same names, distinct values for the
// ADDRESS_LINE_16 / VPP_VPE_DROP_ENABLE pair (Pitfall 2).
#define CTRL_ADDRESS_LINE_16          0x01
#define CTRL_VPP_A9_ENABLE            0x02
#define CTRL_VPE_ENABLE               0x04
#define CTRL_VPP_P1_ENABLE            0x08
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40
#define CTRL_VPP_REGULATOR_ENABLE     0x80
#define CTRL_VPP_VPE_DROP_ENABLE      0x100
#endif

// ---- Section 2b: EPROM high-voltage composite masks (EPROM_HV_*) -------
// Phase 142 / D-07 (Claude's discretion, resolved default taken). Placed
// here, beside the CTRL_* bits they are built from, rather than in
// eprom.h / eprom_params.h: both eprom.cpp and memory.cpp already include
// this header, and a composite defined next to its own bit definitions
// cannot drift from them.
//
//   - EPROM_-scoped naming: the native warning watermark
//     (check_build_warnings.py) sits at 1166 with ZERO headroom, and every
//     one of those 1166 recorded warnings is a macro redefinition. A
//     generic composite name (e.g. HV_ROUTE_MASK) risks colliding with an
//     ArduinoFake or pgmspace macro and turning that live gate RED; the
//     EPROM_ prefix keeps this pair scoped to the EPROM family that owns
//     it (memory.cpp serves every protocol, not just EPROM).
//   - These are LOGICAL masks. Their physical effect on the wire is
//     produced by rurp_map_ctrl_reg_for_hardware_revision() at the point
//     of the actual register write — this header defines what the
//     firmware INTENDS, not the physical bit pattern.
//   - Per-variant values, both composites, both build variants:
//       EPROM_HV_ROUTE_MASK    = 0x81  (legacy: 0x80 | 0x01)
//                              = 0x180 (wide:   0x80 | 0x100)
//       EPROM_HV_ALL_OFF_MASK  = 0x87  (legacy: 0x80 | 0x01 | 0x02 | 0x04)
//                              = 0x186 (wide:   0x80 | 0x100 | 0x02 | 0x04)
//   - On the legacy (!HARDWARE_REVISION) arm, CTRL_VPP_VPE_DROP_ENABLE IS
//     CTRL_ADDRESS_LINE_16 (see :76 above) — a genuine macro alias, not a
//     coincidence. Both composites therefore also clear A16 on that arm.
//     Harmless here: both composites are used only to DISABLE the HV
//     route, and clearing an address line as a side effect of a disable
//     changes nothing about VPP/VPE state.
//   - CTRL_VPP_P1_ENABLE is DELIBERATELY ABSENT from EPROM_HV_ALL_OFF_MASK,
//     for two independent reasons:
//       (a) eprom_internal_set_control_register() (eprom.cpp) strips
//           CTRL_VPE_ENABLE from a caller's mask and substitutes
//           CTRL_VPP_P1_ENABLE whenever using_p1_as_vpp(handle) holds.
//           Naming BOTH bits in the all-off composite would leave the
//           physical VPE line never cleared on that substitution path.
//       (b) On Rev 2-class hardware, logical CTRL_ADDRESS_LINE_18 and
//           logical CTRL_VPP_P1_ENABLE collapse onto the same physical
//           bit 0x08 (see CTRL_ADDRESS_LINE_18_REV2 below). Naming P1
//           buys no additional physical guarantee anyway (correction C-4).
//   - A PRESERVE/HOLD mask (as opposed to an all-off mask) can NOT be a
//     #define: its drop-bit membership depends on a runtime hardware
//     revision read and on handle->pins, neither of which the
//     preprocessor can see. That conditional stays exactly where it is,
//     inside mem_util_calculate_top_address_register.
//   - #define (NOT constexpr), per the same 0-B-until-referenced rule
//     already recorded at :63-64 above — a composite that nothing calls
//     costs 0 B in the .hex.
//   - No bitwise-OR composite #define existed anywhere in this header
//     before this pair. This establishes a new form rather than
//     following an existing one; the nearest in-tree precedent is a
//     single-token alias (e.g. :76, :116, :128 above), not a composite.
#define EPROM_HV_ROUTE_MASK    (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE)
#define EPROM_HV_ALL_OFF_MASK  (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE)

#define CTRL_ADDRESS_LINE_13          0x20  // reserved — no current call-site

// ---- Section 3: Per-rev variants (CTRL_*_REV1 / CTRL_*_REV2) -----------
// Mirrors rurp_shield.h:70-94 VERBATIM with suffix-family rename per
// RESEARCH "State of the Art" deprecation table.

#ifdef HARDWARE_REVISION
// REV 1
#define CTRL_VPP_VPE_DROP_ENABLE_REV1      0x01
#define CTRL_VPP_A9_ENABLE_REV1            0x02
#define CTRL_VPE_ENABLE_REV1               0x04
#define CTRL_VPP_P1_ENABLE_REV1            0x08
#define CTRL_ADDRESS_LINE_17_REV1          0x10
#define CTRL_ADDRESS_LINE_18_REV1          0x20
#define CTRL_READ_WRITE_REV1               0x40
#define CTRL_VPP_REGULATOR_ENABLE_REV1     0x80

#define CTRL_ADDRESS_LINE_16_REV1          CTRL_VPP_VPE_DROP_ENABLE_REV1

// REV 2
#define CTRL_VPP_VPE_DROP_ENABLE_REV2      0x01
#define CTRL_VPP_A9_ENABLE_REV2            0x02
#define CTRL_VPE_ENABLE_REV2               0x04
#define CTRL_VPP_P1_ENABLE_REV2            0x08
#define CTRL_ADDRESS_LINE_17_REV2          0x10
#define CTRL_ADDRESS_LINE_16_REV2          0x20
#define CTRL_READ_WRITE_REV2               0x40
#define CTRL_VPP_REGULATOR_ENABLE_REV2     0x80

#define CTRL_ADDRESS_LINE_18_REV2          CTRL_VPP_P1_ENABLE_REV2
#endif

#ifdef __cplusplus
}
#endif

#endif // __RURP_PINOUT_H__
