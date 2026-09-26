---
phase: 01-safety-closure-intel-flash-vpp-28c-chip-id
verified: 2026-05-12T08:00:00Z
status: passed
score: 5/5
overrides_applied: 0
---

# Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) — Verification Report

**Phase Goal:** Close v1.0 audit-gaps WARNING-1 (Intel-flash REQ-SAF-01 partial — missing VPP ADC compare in `flash_intel_write_init`) and WARNING-2 (REQ-SAF-02 forward-compat for AT28C 5V EEPROM — `eeprom_28c.cpp` must honor `handle->chip_id`). Cover both via Unity tests on `[env:native]` without touching the shared dispatch suite.
**Verified:** 2026-05-12T08:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `flash_intel_write_init` calls `rurp_read_voltage_mv()` and aborts with the existing voltage error code if measured VPP is below the chip's `vpp` setpoint (minus tolerance) before the first write command — REQ-SAF-01 holds for all 39 algorithm=0x10 Intel-flash chips | VERIFIED | `flash_intel_check_vpp` static helper at `flash_intel.cpp:25-50` reads `rurp_read_voltage_mv()`, checks `< vpp_mv * 95 / 100` (warning) and `> vpp_mv + 500` (error), called from `flash_intel_write_init` at line 77 — before `chip_id` branch at line 86 and before any write command |
| 2 | `eeprom28c_write_init` honours `handle->chip_id` when non-zero (matching ID proceeds, mismatching ID aborts), so REQ-SAF-02 holds the moment any algorithm=0x0D entry gains a `chip_id_value` | VERIFIED | `eeprom28c_check_chip_id` static helper at `eeprom_28c.cpp:55-77` performs A9-12V identification and compares; called from `eeprom28c_write_init` at line 83, gated on `handle->chip_id > 0` (line 82), and placed BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)` (line 91) |
| 3 | A Unity test on `[env:native]` proves the new Intel-flash VPP check: low-VPP path returns the voltage error code, nominal-VPP path proceeds | VERIFIED | `test_flash_intel_low_vpp_warns` and `test_flash_intel_vpp_nominal_proceeds` in `test_flash_intel_vpp.cpp`; `pio test -e native` reports PASSED for both; actual suite exit: 6/6 PASSED (includes post-review regression test) |
| 4 | A Unity test on `[env:native]` proves the new 28C chip-ID check: matching fake chip-ID proceeds, mismatching aborts | VERIFIED | `test_eeprom28c_matching_chip_id_proceeds` and `test_eeprom28c_mismatching_chip_id_errors` in `test_eeprom28c_chip_id.cpp`; suite exit: 4/4 PASSED |
| 5 | All pre-existing dispatch / handler Unity tests still pass (no regression in the 15 v1.0 tests) | VERIFIED | `native/avr/test_dispatch` suite: 15/15 PASSED; `firestarter/test/native/avr/test_dispatch/` directory unchanged from v1.0 (D-10 + D-11 confirmed by `git -C firestarter diff` returning 0 lines) |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/flash_intel.cpp` | `static flash_intel_check_vpp` helper + call-site in `flash_intel_write_init` | VERIFIED | Helper at lines 25-50; call-site at line 77; `grep -c "^static void flash_intel_check_vpp"` = 1 |
| `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` | Unity suite — 5 RUN_TEST cases for SAF-04 (nominal / low / high / FORCE / REV0) | VERIFIED | 6 RUN_TEST cases (5 original + 1 post-review CR-01 regression test); all 6 PASSED |
| `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` | Suite-local stubs with mockable `rurp_read_voltage_mv` + `rurp_get_hardware_revision` | VERIFIED | `set_mock_vpp_mv` at line 104, `set_mock_hw_rev` at line 122 (inside `#ifdef HARDWARE_REVISION`); TU-private statics `s_mock_vpp_mv` and `s_mock_hw_rev` |
| `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h` | Host shim for AVR PROGMEM macros | VERIFIED | File exists with `_AVR_PGMSPACE_H_STUB_` include guard |
| `firestarter/src/proms/eeprom_28c.cpp` | `static eeprom28c_check_chip_id` helper + call-site BEFORE `EEPROM_SDP_DISABLE` | VERIFIED | Helper at lines 55-77; call-site at lines 82-87; `grep -c "^static void eeprom28c_check_chip_id"` = 1 |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` | Unity suite — 4 RUN_TEST cases for SAF-05 (matching / mismatching / zero-skip / FORCE) | VERIFIED | 4 RUN_TEST cases; all 4 PASSED |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` | Byte-identical to test_dispatch's stubs (no rurp_* mocking needed; M2 pattern) | VERIFIED | Byte-identical to dispatch suite (no `set_mock_*` setters); `rurp_read_voltage_mv` returns 0 (no-op) |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h` | Host shim for AVR PROGMEM macros | VERIFIED | File exists with `_AVR_PGMSPACE_H_STUB_` include guard |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `flash_intel_write_init` | `flash_intel_check_vpp` | Direct C call at line 77, after `delay(500)` (line 76), before `handle->chip_id > 0` (line 86) | VERIFIED | Line ordering confirmed: delay(500)=76, flash_intel_check_vpp=77, chip_id>0=86 — strictly ascending |
| `flash_intel_check_vpp` | `rurp_read_voltage_mv()` | Free-function call at `flash_intel.cpp:35` | VERIFIED | `uint16_t vpp_mv = rurp_read_voltage_mv();` present; resolved against `host_stubs.cpp` on native (mockable via `set_mock_vpp_mv`) |
| `flash_intel_write_init` early-return | `REGULATOR | P1_VPP_ENABLE` clear | `firestarter_set_control_register` call before `return` at lines 83-85 | VERIFIED | CR-01 fix confirmed at lines 79-85; test `test_flash_intel_high_vpp_error_clears_regulator` asserts `s_ctrl_writes_with_p1_low > 0` and `s_last_ctrl_state == false` — PASSED |
| `test_flash_intel_vpp.cpp` | `host_stubs.cpp` | `extern "C" void set_mock_vpp_mv(uint16_t)` and `void set_mock_hw_rev(uint8_t)` | VERIFIED | Forward declarations at lines 33-34 in test TU; definitions in host_stubs.cpp lines 104, 122 |
| `eeprom28c_write_init` | `eeprom28c_check_chip_id` | Direct C call at line 83, gated on `chip_id > 0` (line 82), BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)` (line 91) | VERIFIED | Line ordering: helper definition=55, call-site=83, SDP_DISABLE=91 — check precedes SDP-disable by 8 lines inside `eeprom28c_write_init` |
| `eeprom28c_check_chip_id` | `handle->firestarter_get_data` | Function-pointer dispatch at lines 70-71 (reads `mfr_addr` and `mfr_addr + 1`) | VERIFIED | `handle->firestarter_get_data(handle, mfr_addr) << 8` at line 70; `chip_id |= handle->firestarter_get_data(handle, mfr_addr + 1)` at line 71; mocked via `mock_get_data_scripted` in tests |
| `test_eeprom28c_chip_id.cpp` | `mock_get_data_scripted` | `h.firestarter_get_data = mock_get_data_scripted` re-assigned after `configure_memory()` | VERIFIED | Pattern at lines 108, 123, 143, 163 (post-configure reassignment); `s_mock_byte_idx` used in `test_eeprom28c_zero_chip_id_skips_check` to prove helper not invoked |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `flash_intel_check_vpp` | `vpp_mv` (measured) | `rurp_read_voltage_mv()` — mocked in tests via `set_mock_vpp_mv()`; on AVR reads hardware ADC | Yes — mock injects controlled values; 3 distinct band regions tested (nominal 12000, low 11000, high 12700) | FLOWING |
| `eeprom28c_check_chip_id` | `chip_id` (read back) | `handle->firestarter_get_data(handle, mfr_addr)` and `...+1` — mocked via `s_mock_bytes[]` in tests | Yes — scripted bytes `{0x1F, 0x08}` and `{0xDE, 0xAD}` produce both match and mismatch paths | FLOWING |
| `flash_intel_write_init` early-return | `handle->response_code` | Set by `flash_intel_check_vpp` via `firestarter_response_format` macro | Yes — macro sets `handle->response_code` to `RESPONSE_CODE_ERROR` or `RESPONSE_CODE_WARNING` as appropriate | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full native suite PASSES (25 tests) | `cd firestarter && pio test -e native` | 25 test cases: 25 succeeded | PASS |
| Dispatch suite unchanged (15/15) | `pio test -e native` (test_dispatch env) | `native/avr/test_dispatch [PASSED]` — 15/15 | PASS |
| VPP SAF-04 suite (6/6) | `pio test -e native` (test_flash_intel_vpp env) | `native/avr/test_flash_intel_vpp [PASSED]` — 6/6 | PASS |
| Chip-ID SAF-05 suite (4/4) | `pio test -e native` (test_eeprom28c_chip_id env) | `native/avr/test_eeprom28c_chip_id [PASSED]` — 4/4 | PASS |
| CR-01 regression: VPP error clears regulator | `test_flash_intel_high_vpp_error_clears_regulator` in suite | PASSED — asserts `s_ctrl_writes_with_p1_low > 0` and final write state=false | PASS |
| CR-02 regression: `mem_size < 64` underflow guard | `eeprom_28c.cpp:56-60` guard present | `if (handle->mem_size < 64)` fires before address derivation | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| SAF-04 | 01-01-PLAN.md | `flash_intel_write_init` calls `rurp_read_voltage_mv()` and aborts if measured VPP is below tolerance before write command | SATISFIED | `flash_intel_check_vpp` static helper at `flash_intel.cpp:25-50`; called at line 77; 6 Unity tests PASS |
| SAF-05 | 01-02-PLAN.md | `eeprom28c_write_init` honours `handle->chip_id` when non-zero | SATISFIED | `eeprom28c_check_chip_id` static helper at `eeprom_28c.cpp:55-77`; gated on `chip_id > 0`, called before SDP-disable; 4 Unity tests PASS |
| SAF-06 | 01-01-PLAN.md + 01-02-PLAN.md | Unity tests on `[env:native]` covering both checks | SATISFIED | `test_flash_intel_vpp/` (6 tests) + `test_eeprom28c_chip_id/` (4 tests); all 10 PASS; dispatch regression 15/15 PASS; total native suite 25/25 PASS |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `flash_intel.cpp:39` | 39 | `int response_code` — local variable shadows outer scope idiom; same pattern as pre-existing `flash_intel_check_chip_id:152` | Info | Not a defect; consistent with codebase style |
| `eeprom_28c.cpp:23` | 25 | `const byte_flip_t EEPROM_SDP_DISABLE[]` missing `static` qualifier (pre-existing, noted in review WR-01 as IN-01) | Info | In C++ namespace-scope `const` has internal linkage; no ODR risk; pre-existing style |
| `test_eeprom28c_chip_id.cpp:108,123,143,163` | multiple | `h.firestarter_get_data = mock_get_data_scripted` reassigned after `configure_memory()` (4 repetitions) | Warning | Fragile coupling to dispatcher internals; documented in test docstrings; noted in review WR-03; not a phase-blocking issue |

No `TBD`, `FIXME`, or `XXX` markers found in any file modified by this phase. No unreferenced debt markers.

No stub patterns (empty returns, hardcoded empty arrays, placeholder comments) found in the production code changes.

---

### Human Verification Required

None. The phase scope explicitly excludes physical-hardware programming. The canonical sign-off path is the native suite (25/25 PASSED) plus code review. Hardware validation is deferred to Phase 4 (HW-05: physical RURP shield with Intel-family flash chip confirming the new VPP ADC compare aborts a deliberately-underpowered run).

Physical-hardware tests (HW-05) are tracked as Phase 4 requirements and are not blocking Phase 1 verification.

---

### Post-Review Fixes (Context Signals)

The code review (`01-REVIEW.md`, reviewed 2026-05-12T06:19:50Z) surfaced two critical findings fixed before this verification was run:

**CR-01 (safety regression in `flash_intel_write_init`):** The original VPP error early-return left `REGULATOR | P1_VPP_ENABLE` asserted, exposing socket pin 1 to 12V after an over-voltage detection. Fixed in `firestarter` commit `f6480f2`: the early-return path at `flash_intel.cpp:79-85` now calls `firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0)` before returning. A regression test `test_flash_intel_high_vpp_error_clears_regulator` was added (6th test in the suite) that records control-register writes and asserts the regulator was driven low — this test PASSES.

The same fix was applied to the chip-id early-return path at `flash_intel.cpp:88-91` (WR-01 from the review).

**CR-02 (integer underflow in `eeprom28c_check_chip_id`):** `uint32_t mfr_addr = handle->mem_size - 64` was unconditional; `mem_size == 0` wraps to `0xFFFFFFC0` and would drive 12V on A9 of an arbitrary address. Fixed in `firestarter` commit `4b57656`: a guard at `eeprom_28c.cpp:56-60` checks `mem_size < 64` and returns `RESPONSE_CODE_ERROR` (or WARNING with FORCE) before any address derivation.

Both fixes were recorded in meta-repo commit `83c37b7`. The native suite result of 25/25 PASSED reflects the corrected code.

---

### Gaps Summary

No gaps. All 5 roadmap success criteria are VERIFIED. All 3 phase requirements (SAF-04, SAF-05, SAF-06) are SATISFIED. The native test suite passes cleanly at 25/25 with no regressions. Both post-review critical fixes (CR-01 safety regression, CR-02 integer underflow) are in the current codebase and covered by tests.

---

_Verified: 2026-05-12T08:00:00Z_
_Verifier: Claude (gsd-verifier)_
