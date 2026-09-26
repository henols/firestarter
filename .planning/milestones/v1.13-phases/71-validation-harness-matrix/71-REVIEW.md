---
phase: 71-validation-harness-matrix
reviewed: 2026-06-16T00:00:00Z
depth: standard
files_reviewed: 31
files_reviewed_list:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tools/gen_validation_header.py
  - firestarter_app/tools/validation_matrix_spec.json
  - firestarter/platformio.ini
  - firestarter/test/native/avr/_shared/host_stubs_common.inc
  - firestarter/test/native/avr/_shared/validation_matrix.h
  - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter/test/native/avr/test_val_eprom/host_stubs.cpp
  - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
  - firestarter/test/native/avr/test_val_eeprom28c/host_stubs.cpp
  - firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp
  - firestarter/test/native/avr/test_val_flash3/host_stubs.cpp
  - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
  - firestarter/test/native/avr/test_val_flash4/host_stubs.cpp
  - firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp
  - firestarter/test/native/avr/test_val_flash_intel/host_stubs.cpp
  - firestarter/test/native/avr/test_val_sram/test_val_sram.cpp
  - firestarter/test/native/avr/test_val_sram/host_stubs.cpp
  - firestarter_app/tests/test_check_dispatch_invariants.py
  - firestarter_app/tests/test_gen_validation_header.py
  - firestarter_app/tests/test_matrix_schema.py
  - firestarter_app/tests/test_matrix_artifact.py
  - firestarter_app/tests/test_validate_family_cmd.py
  - firestarter_app/tests/test_validate_oracle.py
  - firestarter_app/tests/test_val_wire_eprom.py
  - firestarter_app/tests/test_val_wire_eeprom28c.py
  - firestarter_app/tests/test_val_wire_flash3.py
  - firestarter_app/tests/test_val_wire_flash4.py
  - firestarter_app/tests/test_val_wire_flash_intel.py
  - firestarter_app/tests/test_val_wire_sram.py
findings:
  critical: 2
  warning: 3
  info: 3
  total: 8
status: issues_found
---

# Phase 71: Code Review Report

**Reviewed:** 2026-06-16T00:00:00Z
**Depth:** standard
**Files Reviewed:** 31
**Status:** issues_found

## Summary

Phase 71 introduces the validation harness: Tier-1 native Unity suites with a recording bus stub, Tier-2 host wire round-trip tests, Tier-3 `dev validate-family` CLI runner, an authored spec + codegen pipeline, and extended `check_dispatch.py` VPP invariants.

The Tier-1 C++ suites and the Tier-2 wire tests are well-structured. The codegen pipeline and drift gate are correct. Two blockers were found:

1. The Tier-3 oracle in `cli_handlers.py` compares the source-image SHA to itself rather than to the actual readback SHA — the HARN-03 "non-vacuous PASS" property is not provided for the hardware path.
2. `check_dispatch.dispatch()` is missing protocols `0x35` and `0x39`, which the firmware does dispatch to `configure_flash4` (confirmed in `memory.cpp:89`). The validation spec includes these as flash4 protocols, so the host-side dispatch mirror and the spec are inconsistent.

Three warnings cover the deprecated `utcnow()`, a silent recording-buffer overflow in the stub (could silently miss VPP writes in a longer operation path), and two missing SRAM dispatch-level test cases.

---

## Critical Issues

### CR-01: `dev validate-family` oracle always yields PASS — readback SHA is never compared to source SHA

**File:** `firestarter_app/firestarter/cli_handlers.py:1556-1562`

**Issue:** When `write_cycle_eprom` returns 0 (hardware path), the code computes
`evidence_sha = sha256(source_image)` and then calls `_classify_sha_result(evidence_sha, evidence_sha, board)`.
Both arguments are the same object — the SHA is compared to itself.
The comparison is always equal, so `cell_verdict` is always `"PASS"` on the hardware path regardless of what was actually read back from the chip.

The HARN-03 / D-08 "non-vacuous PASS" requirement states the oracle must be falsifiable. The negative-control test in `test_validate_oracle.py` (line 96) tests `write_cycle_eprom` returning `1` (FAIL path), not the `0` (PASS) path — so this bug is invisible to the current test suite for hardware runs.

`write_cycle_eprom` internally returns 0 only when its own readback SHA matches — the information is available inside that call but is not surfaced into a return value accessible to `dev_validate_family`. The `evidence_sha` is derived from the source image, which is correct for the artifact record, but the classification call uses it as both `readback_sha` and `source_sha`.

**Fix:** `write_cycle_eprom` needs to surface the readback SHA (or the per-run file paths) so `dev_validate_family` can do a real comparison. Until the operator API is extended, the simplest correct approach is to trust `write_cycle_eprom`'s return code directly and drop the redundant `_classify_sha_result` call for the `verdict_int == 0` branch — the call already carries the authoritative signal:

```python
# Map verdict to oracle classification (Leonardo = authoritative).
if verdict_int == 0:
    # write_cycle_eprom's 0 return is the authoritative PASS signal.
    # Leonardo is the authoritative board; other boards are advisory.
    cell_verdict = "PASS" if board == _AUTHORITATIVE_PASS_BOARD else "advisory"
elif verdict_int == 1:
    cell_verdict = "FAIL"
else:
    cell_verdict = "SKIP-deferred"  # hw-error → deferred
```

Alternatively, extend `write_cycle_eprom` to return the readback SHA so the comparison can be done properly.

---

### CR-02: `check_dispatch.dispatch()` missing flash4 protocols 0x35 and 0x39 — diverges from firmware

**File:** `firestarter_app/tools/check_dispatch.py:133-157`

**Issue:** The firmware `memory.cpp:89` dispatches `protocol ∈ {0x05, 0x35, 0x39}` to `configure_flash4`. The host-side `dispatch()` mirror handles only `0x05` (line 141); `0x35` (53) and `0x39` (57) fall through to the `protocol != 0` guard at line 149 and are returned as `"not_implemented"`.

The validation spec (`validation_matrix_spec.json`) explicitly lists `[5, 53, 57]` as flash4 protocols (i.e. includes 0x35 and 0x39). The Tier-1 C++ tests for flash4 also directly test 0x35 and 0x39 (test_val_flash4.cpp lines 106-158). But the check_dispatch host mirror and the `_ALGO_MEM_TYPE` table both omit these two protocols.

Consequence: if any chip with `algorithm=0x35` or `algorithm=0x39` is ever added to chip_database.json, `check_dispatch.py` would flag it as a gate failure (`not_implemented` for a supported chip), even though the firmware would handle it correctly. The validation harness would also misclassify it. The HARN-02 generated header does include 0x35 and 0x39 rows — making it inconsistent with what check_dispatch can verify.

Note: `build_db.py` explicitly excludes 0x35 and 0x39 from its `KNOWN_PROTOCOLS` (v1.11 DEC-05) because no DB chip uses them today. The spec should not declare them as validated flash4 protocols if the host-side toolchain cannot verify them.

**Fix option A (minimal):** Remove 0x35 and 0x39 from `validation_matrix_spec.json` protocols for the flash4 family (and regenerate `validation_matrix.h`). This aligns the spec with the host-side KNOWN_PROTOCOLS and check_dispatch reality.

**Fix option B (correct the mirror):** Add 0x35 and 0x39 to `check_dispatch.dispatch()` to match firmware truth:

```python
if protocol in (0x05, 0x35, 0x39):   # flash4: FLASH_AMD_STD, FLASH_EEPROM, FLASH_EEPROM2
    return "configure_flash4"
```

Also add them to `_ALGO_MEM_TYPE` in check_dispatch.py:

```python
0x35: 5,  # FLASH_EEPROM     → TYPE_FLASH_TYPE_4
0x39: 5,  # FLASH_EEPROM2    → TYPE_FLASH_TYPE_4
```

Option B makes the host mirror truthful at the cost of also adding them to KNOWN_PROTOCOLS so that check_dispatch does not classify them as invalid. This requires coordinating with build_db.py and database.py.

---

## Warnings

### WR-01: `datetime.utcnow()` is deprecated

**File:** `firestarter_app/firestarter/cli_handlers.py:1356`

**Issue:** `datetime.datetime.utcnow()` is deprecated since Python 3.12 and scheduled for removal. In Python 3.12+ it emits a `DeprecationWarning`.

```python
"generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
```

**Fix:**
```python
"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
```

---

### WR-02: Recording-buffer silent-discard — VPP detection may give false PASS if overflow occurs

**File:** `firestarter/test/native/avr/_shared/host_stubs_common.inc:70-74`

**Issue:** The recording buffer has a hard limit of 256 entries (`HOST_STUBS_MAX_RECORDING`). When the buffer is full, subsequent `rurp_write_to_register` calls are silently discarded without setting an overflow flag:

```c
if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
    s_bus_recording[s_bus_recording_count].reg  = reg;
    s_bus_recording[s_bus_recording_count].data = (uint8_t)data;
    s_bus_recording_count++;
}
// No else — overflow is silently dropped
```

The EPROM positive tests call `firestarter_operation_init` after `configure_memory`. If the VPP write happens to be entry #257 or later in the call chain (because the firmware code has been extended, or `mem_size` changes), `recording_has_vpp_enable` would return false and the positive assertion would fail or (worse) give a false PASS if the assertion is `TEST_ASSERT_TRUE`.

Currently with `mem_size=65536` and `runs=1`, the buffer is not expected to overflow. But the failure mode is silent — there is no test-level diagnostic when it does.

**Fix:** Add an overflow sentinel and assert it is not set in each test's `tearDown`:

```c
static bool s_bus_recording_overflow = false;

extern "C" void clear_bus_recording() {
    s_bus_recording_count = 0;
    s_bus_recording_overflow = false;
}
extern "C" bool bus_recording_overflowed() { return s_bus_recording_overflow; }

// In rurp_write_to_register:
if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
    ...
} else {
    s_bus_recording_overflow = true;
}
```

Each test suite's `tearDown` should assert `!bus_recording_overflowed()`.

---

### WR-03: SRAM Tier-1 full-dispatch tests cover only 2 of 4 protocols

**File:** `firestarter/test/native/avr/test_val_sram/test_val_sram.cpp:120-150`

**Issue:** The spec declares four SRAM protocols: `{0x0E, 0x27, 0x28, 0x29}`. The direct handler tests (lines 79-113) do test all four via `configure_sram` directly. However the full `configure_memory` dispatch tests (lines 120-150) only cover `0x0E` and `0x27`:

```c
RUN_TEST(test_sram_dispatch_0x0E_no_vpp_no_init);
RUN_TEST(test_sram_dispatch_0x27_no_vpp_no_init);
```

Protocols `0x28` and `0x29` have no corresponding dispatch-level assertion that `configure_memory` routes correctly and does not engage VPP. The BLOCKER-2 "SRAM never reaches VPP" guarantee is not exercised end-to-end for two of the four SRAM protocols.

**Fix:** Add `test_sram_dispatch_0x28_no_vpp_no_init` and `test_sram_dispatch_0x29_no_vpp_no_init` following the same pattern as `test_sram_dispatch_0x27_no_vpp_no_init`, and register them in `main()`.

---

## Info

### IN-01: Spec declares protocols 0x35 and 0x39 that build_db.py explicitly excludes

**File:** `firestarter_app/tools/validation_matrix_spec.json:75`

**Issue:** The flash4 family entry lists `"protocols": [5, 53, 57]` (0x05, 0x35, 0x39). However, `build_db.py` explicitly excludes 0x35 and 0x39 from `KNOWN_PROTOCOLS` with the comment:
> "0x35 (IC2_ALG_ITE — ITE EC MCU TQFP128; no DIP memory chips) and 0x39 (phantom — no IC2_ALG constant) removed in v1.11 DEC-05."

No chip in the current database uses these protocols. Including them in the spec creates a false impression that the harness validates firmware behavior for chips that do not exist in the database. The generated header (`validation_matrix.h`) emits rows for 0x35 and 0x39 (rows 7 and 8), but the Tier-2 wire tests can never exercise them because `EpromDatabase` holds no such chips.

**Fix:** Remove 0x35 and 0x39 from the flash4 protocols entry in the spec. Regenerate `validation_matrix.h`. This aligns spec, host toolchain, and DB state. If 0x35/0x39 chips are ever added to the DB, the spec can be extended then.

---

### IN-02: `test_matrix_schema.py` hardcodes protocol-id set including 0x35 and 0x39

**File:** `firestarter_app/tests/test_matrix_schema.py:153-164`

**Issue:** `test_protocol_ids_cover_expected_set` asserts the union of all spec protocols equals exactly `{7, 8, 11, 13, 6, 5, 53, 57, 16, 14, 39, 40, 41}`. The magic set `53` and `57` correspond to the 0x35/0x39 protocols noted in IN-01. If the spec is corrected to remove 0x35/0x39, this test must also be updated; if not, it becomes a spec-enforcement lock that prevents the correction. This is coupling, not validation.

**Fix:** After resolving IN-01, update the expected set to `{7, 8, 11, 13, 6, 5, 16, 14, 39, 40, 41}` (removing 53 and 57).

---

### IN-03: `_EVIDENCE_SHA_SOFTWARE_SENTINEL` constant is defined but unused

**File:** `firestarter_app/firestarter/cli_handlers.py:1261-1263`

**Issue:** The constant `_EVIDENCE_SHA_SOFTWARE_SENTINEL` is computed at module level:

```python
_EVIDENCE_SHA_SOFTWARE_SENTINEL: str = hashlib.sha256(
    b"tier-software-no-file"
).hexdigest()
```

It is never referenced anywhere in the module — not in `_emit_skip_deferred_artifact`, `_write_artifact`, or any other function. The skip-deferred cells set `evidence_sha: None`, not this sentinel. Dead code that costs an unnecessary `hashlib.sha256` computation on module import.

**Fix:** Remove the constant or use it in place of `None` for software-only cells (whichever matches the intended design).

---

_Reviewed: 2026-06-16T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
