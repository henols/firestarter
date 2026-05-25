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
// Consumed by rurp_detect_hardware_revision() in rurp_hw_rev_utils.h to decode
// the R41-on-A3 detect divider into a per-rev enum. Voltage-band math sourced
// from Phase 34 RESEARCH §ADC Voltage Band Math + the §9 per-rev band table in
// .planning/v1.7-SHIELD-REVS.md (D-03 + D-11). Values picked with strict
// numerical ordering (200 < 220 < 600) per D-11 + a 20-count guard gap between
// the 4k7 ceiling and the 10k floor (reads in [200, 220) → REVISION_UNKNOWN).
// #define (NOT constexpr) per Phase 33 D-07 — preprocessor constants resolve
// at compile time and contribute 0 B to the .hex until referenced.
#ifdef HARDWARE_REVISION
#define ADC_BAND_R41_4K7_HIGH 200  // upper edge of 4k7 bucket (Rev 2.0/2.1/2.2)
#define ADC_BAND_R41_10K_LOW  220  // lower edge of 10k bucket (Rev 2.3); [200, 220) -> REVISION_UNKNOWN
#define ADC_BAND_R41_10K_HIGH 600  // upper edge of 10k bucket; above -> high band / no R41
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
