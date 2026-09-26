---
status: resolved
trigger: "Phase 54 UAT Test 2: firmware reports 'VPP is low: 1.8V < 12.0V' while bench multimeter measures 12.2V on uno328pb / Rev 2.0 shield. Program path stalls. Operator: 'This is a fw bug, it measures 12.2v'"
created: 2026-06-04T16:40:00Z
updated: 2026-08-09
---

## Current Focus

hypothesis: VPP voltage divider math (R1/R2 or ADC reference) produces ~6.8x under-read for uno328pb / Rev 2.0
test: read hw_read_voltage path + divider math + rurp_configuration_t defaults
expecting: a constant scaling error of ~6.8x (12.2 -> 1.8)
next_action: locate and read voltage measurement code

## Symptoms

expected: Firmware reports accurate VPP (~12V) so program path completes
actual: Firmware reports "VPP is low: 1.8V < 12.0V"; bench multimeter reads 12.2V at socket; ratio ~6.8x
errors: "VPP is low: 1.8V < 12.0V"
reproduction: firestarter vpp / id / write -b on W27C512 / uno328pb / Rev 2.0 shield on /dev/ttyUSB0
started: unknown; suspected pre-existing (Phase 54 only touched COBS cap + FW identity)

## Eliminated

- hypothesis: Phase 54 (EVEN-01) introduced the VPP misread
  evidence: git show --stat f8249b8 / c1ae294 — touched only firestarter.h, rurp_serial_utils.{h,cpp}, rurp_shield.h(COBS cap line), firestarter.cpp, operation_utils.cpp, and native test suites. Neither rurp_common.cpp (VPP math) nor VALUE_R1/R2 nor rurp_config_utils.cpp changed. PRE-EXISTING.
  timestamp: 2026-06-04

- hypothesis: The divider math in rurp_read_voltage_mv is itself wrong / overflows
  evidence: Math verified correct. With cfg R1=270000,R2=44000, true 12.2V at A2 ⇒ Vadc=1.71V ⇒ adc≈350, bandgap≈225 ⇒ (350*1100*314000+den/2)/(225*44000) = 12211 mV ≈ 12.2V. 64-bit numerator, no overflow. Rounding correct.
  timestamp: 2026-06-04

- hypothesis: Wrong ADC reference (5V vs 1.1V bandgap) for uno328pb
  evidence: rurp_get_bandgap_adc_reading uses identical ADMUX for ARDUINO_AVR_UNO and ARDUINO_AVR_ATmega328PB (same #if branch, rurp_common.cpp:24). No board-specific divergence. Ratiometric formula cancels VCC.
  timestamp: 2026-06-04

- hypothesis: Per-board (uno328pb / Rev 2.0) conditional R1/R2 constant is wrong
  evidence: grep shows NO board-conditional R1/R2 anywhere. All boards share VALUE_R1=270000 / VALUE_R2=44000 (rurp_shield.h:49-50). Runtime value comes ONLY from EEPROM via rurp_load_config().
  timestamp: 2026-06-04

## Evidence

- timestamp: 2026-06-04
  checked: rurp_common.cpp:52-71 rurp_read_voltage_mv + rurp_shield.h:49-50 defaults
  found: Vin_mV = (Vadc_raw * 1100 * (r1+r2)) / (bandgap_raw * r2). r1/r2 come from rurp_get_config() (EEPROM). Default VALUE_R1=270000, VALUE_R2=44000.
  implication: Reported voltage scales linearly with (r1+r2)/r2. A too-small r1 under-reports proportionally.

- timestamp: 2026-06-04
  checked: numeric simulation of divider (python)
  found: With FW config holding stale R1=1000, R2=44000 but the REAL hardware divider being the correct 270k/44k, a true 12.2V produces reported = 1750 mV ≈ 1.8V. EXACT MATCH to symptom "1.8V".
  implication: The board's EEPROM holds the OLD pre-fix R1≈1000. The 6.8x under-read = (314000/44000)/(45000/44000) ≈ 6.84x.

- timestamp: 2026-06-04
  checked: rurp_config_utils.cpp:22-40 rurp_load_config / rurp_validate_config
  found: Config is read straight from EEPROM (CONFIG_START=48). Defaults (VALUE_R1/R2) are written ONLY when strcmp(config->version, "VER06") != 0. If version already == "VER06", stale r1/r2 are kept untouched.
  implication: The Phase 44 code-default fix (R1 1000→270000) does NOT propagate to an already-calibrated board because CONFIG_VERSION was not bumped. EEPROM is authoritative and stale.

- timestamp: 2026-06-04
  checked: operator bench memory (project_v19_phase44_bug_a_rca.md) + prior-art note in debug context
  found: This exact bench board had a documented "Uno VPP R1=1000→270000 fix" in v1.9/Phase 44. That fix was applied to the code default, not necessarily re-burned to THIS board's EEPROM.
  implication: Strongly corroborates stale-EEPROM-R1=1000 on the uno328pb bench unit.

- timestamp: 2026-06-04
  checked: host readback path firestarter_app/firestarter/codec.py:98-107 (MSG_OK_CFG)
  found: `firestarter config` / hw_get_config (hardware_operations.cpp:107-126) returns live EEPROM r1, r2, override. Renders "R1: {r1}, R2: {r2}".
  implication: Definitive non-destructive bench confirmation: read back R1 on the board. Expected to show R1≈1000 (or some value ≪270000), not 270000.

## Resolution

root_cause: |
  The firmware VPP-measurement MATH and code defaults are correct. The misread is
  caused by a STALE EEPROM calibration value on the uno328pb bench board: its
  rurp_configuration_t.r1 holds the old pre-Phase-44 value (~1000 ohm) instead of
  the correct 270000. rurp_read_voltage_mv (src/boards/rurp_common.cpp:52-71)
  computes Vin = Vadc*1100*(r1+r2)/(bandgap*r2); with r1≈1000 the (r1+r2)/r2 gain
  collapses from 7.14x to ~1.02x, under-reporting a true 12.2V as ~1.75V ≈ 1.8V
  (matches symptom exactly; 6.8x error). The latent FIRMWARE BUG that lets this
  persist is in rurp_validate_config (src/rurp_config_utils.cpp:32-39): defaults
  are re-applied only when config->version != CONFIG_VERSION ("VER06"). The Phase 44
  R1 default change (1000→270000) did NOT bump CONFIG_VERSION, so any board already
  calibrated under VER06 keeps its stale r1 forever — the code "fix" never reaches
  the EEPROM. Result: the program/write path reads 1.8V < 12.0V threshold and stalls
  at the first chunk (0x0200). NOT a Phase 54 / EVEN-01 regression; transport is sound.
fix: ""  # diagnose-only; see Suggested Fix Direction in return
verification: ""  # requires bench: firestarter config readback of R1, or recalibrate
files_changed: []

---

## Session Closure — 2026-08-09

**Closed as a debugging activity.** The investigation is complete: the root cause was
identified, every competing hypothesis eliminated, and the arithmetic shown to reproduce
the `1.8V` symptom exactly. Nothing further is learned by keeping the session open.

**The board-level symptom** (stale `r1` on the uno328pb bench unit) was cleared by
recalibrating that board.

**The latent firmware defect is NOT fixed** and was re-confirmed present on 2026-08-09:
`CONFIG_VERSION` is still `"VER06"` (`include/rurp_shield.h:46`), `VALUE_R1` is still
`270000` (`:49`), and `rurp_validate_config` (`src/rurp_config_utils.cpp:35-43`) still
gates the default re-apply on a version-string mismatch. Any board calibrated under
`VER06` keeps a stale `r1` forever.

That defect is now tracked, with the fix options and the calibration-loss trade-off spelled
out, at:

  `.planning/todos/pending/config-version-not-bumped-strands-stale-eeprom-calibration.md`

It carries `needs_decision: true` — bumping `CONFIG_VERSION` would wipe every board's real
calibration, so the repair is an operator choice, not a mechanical fix.
