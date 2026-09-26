---
phase: 01-safety-closure-intel-flash-vpp-28c-chip-id
reviewed: 2026-05-12T06:19:50Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - firestarter/src/proms/flash_intel.cpp
  - firestarter/src/proms/eeprom_28c.cpp
  - firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp
  - firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp
  - firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h
  - firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp
  - firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp
  - firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h
  - firestarter/.gitignore
findings:
  critical: 2
  warning: 5
  info: 4
  total: 11
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-05-12T06:19:50Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

The two production changes (`flash_intel_check_vpp`, `eeprom28c_check_chip_id`) deliver the SAF-04 / SAF-05 / SAF-06 closure intent, but a serious **safety regression** has been introduced in the Intel-flash path: when `flash_intel_check_vpp` raises `RESPONSE_CODE_ERROR`, the caller `flash_intel_write_init` early-returns **without** disabling the boost regulator, leaving 12 V P1_VPP_ENABLE applied to the socket. The whole purpose of the pre-pulse VPP check is to abort before damaging silicon — the current control flow detects the unsafe condition and then leaves the unsafe condition asserted. This is a BLOCKER (CR-01). The same shape exists for the chip-id error path that was already there pre-phase, so this is a regression amplification rather than a pure introduction, but the new VPP path makes it reachable in a new failure mode.

The 28C path (`eeprom28c_check_chip_id`) is safer because the regulator clear happens unconditionally before the chip-id compare; however, the helper has one ordering issue (CR-02): on the FORCE-downgraded path the regulator is dropped before the SDP-disable sequence resumes, which is correct, but on the **normal mismatch ERROR** path the SDP-disable sequence is the wrong-data write that follows after early-return. Re-reading shows this is OK because the early-return prevents the SDP write — but there is a related dataflow concern around `mem_size < 64` callers, called out below.

The test scaffolding is generally sound; the documented `firestarter_get_data` reassignment workaround after `configure_memory()` is fragile but explicitly called out in the test docstrings. Several `.gitignore` and dispatcher-coupling concerns are listed as warnings.

## Critical Issues

### CR-01: VPP error path leaves 12 V applied to socket pin 1 (safety regression)

**File:** `firestarter/src/proms/flash_intel.cpp:39-50, 74-80`

**Issue:**
`flash_intel_check_vpp` deliberately omits the regulator-clear at exit (line 49 comment: "NO regulator clear — caller continues to use REGULATOR | P1_VPP_ENABLE through the write pulse"). When the function sets `RESPONSE_CODE_ERROR` (non-FORCE high-VPP path, line 40-43), the caller `flash_intel_write_init` checks `handle->response_code == RESPONSE_CODE_ERROR` and `return`s immediately at line 78-80 — **without** turning off `REGULATOR | P1_VPP_ENABLE`. The framework's housekeeping (`operation_utils.cpp:229-235`) skips the END phase when INIT errors, so `flash_intel_cleanup` (which would clear the regulator) is never invoked. Net result: when the firmware detects that VPP is dangerously above the chip's rated maximum (e.g. 14 V on a 12 V part), it logs the error and then continues to apply that dangerous voltage to the socket indefinitely — the opposite of what a pre-pulse safety check is supposed to do.

Compare with the v1.0 `eprom_check_vpp` (eprom.cpp:231) which unconditionally clears `REGULATOR | VPE_TO_VPP` at every exit, including the error path; that pattern is correct and safe.

The new chip-id check at line 81-86 has the same shape and inherits the same defect (regulator stays on after chip-id ERROR), but the VPP-check error path is the new reachable failure mode introduced by this phase.

**Fix:**
Either clear the regulator inside `flash_intel_check_vpp` before setting ERROR, or clear it in `flash_intel_write_init` at every early-return after the regulator was enabled. The second is preferable because it keeps the "caller owns the regulator" invariant the helper comments documents:

```cpp
void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    flash_intel_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
        return;
    }
    if (handle->chip_id > 0) {
        flash_intel_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
            return;
        }
    }
    // ... rest unchanged
}
```

Add a regression test that asserts the regulator was driven low (record control-register writes in the host stub) after a high-VPP ERROR, so the silent-regulator-leak class of bug can never recur without a failing test. The current suite asserts only `response_code` — that is what allowed this defect to ship.

---

### CR-02: AT28C chip-id A9 address derivation breaks for `mem_size < 64`

**File:** `firestarter/src/proms/eeprom_28c.cpp:55-69`

**Issue:**
`uint32_t mfr_addr = handle->mem_size - 64;` is unconditional. `mem_size` is `uint32_t` (firestarter.h:83). If `mem_size == 0` (uninitialized handle, malformed JSON command, or a non-28C chip mistakenly routed here) the subtraction wraps to `0xFFFFFFC0` and the helper drives a 32-bit address into `firestarter_get_data` → `memory_get_data` → `mem_util_set_address`, which masks the top bits but still produces a deterministic-yet-arbitrary address with `A9_VPP_ENABLE` asserted. That is, the firmware will assert 12 V on A9 of an unspecified address while reading two bytes whose contents become the "chip id" used for the safety compare. For any chip with `mem_size < 64` this is the same defect. The gate `if (handle->chip_id > 0)` (line 74) does not block this — `chip_id` is supplied by the host independently of `mem_size`.

The 28C-family parts in the DB all have `mem_size ∈ {2048, 8192, 16384, 32768}` so this is not reachable through a well-formed `algorithm: 0x0D` chip selection. It becomes reachable when a hand-crafted JSON command supplies `algorithm: 0x0D` with `memory-size: 0` (or `< 64`) and a non-zero `chip-id`. With 12 V on A9, depending on the chip's logical mapping of address bits, this could violate datasheet `V_IH(max)`.

**Fix:**
Guard against the underflow before the subtraction, and fail closed:

```cpp
static void eeprom28c_check_chip_id(firestarter_handle_t* handle) {
    debug("Check chip ID (28C)");
    if (handle->mem_size < 64) {
        firestarter_error_response("28C: mem_size < 64, cannot derive chip-id address");
        return;
    }
    handle->firestarter_set_control_register(handle, REGULATOR, 1);
    // ...
}
```

Add a Unity test (`test_eeprom28c_small_memsize_errors`) that drives `mem_size = 0` with `chip_id != 0` and asserts `RESPONSE_CODE_ERROR` without any data reads.

## Warnings

### WR-01: Chip-id ERROR path in `flash_intel_write_init` also leaks regulator state

**File:** `firestarter/src/proms/flash_intel.cpp:81-86`

**Issue:**
Pre-existing shape, but now sits right next to CR-01 and shares the same defect surface: when `flash_intel_check_chip_id` (called from the write-init path with `REGULATOR | P1_VPP_ENABLE` already asserted by the caller) raises ERROR for an ID mismatch, the early-return at line 83-85 leaks the regulator. While the original v1.0 code only ran this check from a separate `CMD_CHECK_CHIP_ID` flow (where there was no regulator state to leak), wiring it into `flash_intel_write_init` makes the leak reachable.

**Fix:**
Clear the regulator at the early-return, same shape as CR-01:
```cpp
if (handle->chip_id > 0) {
    flash_intel_check_chip_id(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
        return;
    }
}
```

---

### WR-02: REV0 skip path emits a WARNING but proceeds to write at uncertified VPP

**File:** `firestarter/src/proms/flash_intel.cpp:27-32`

**Issue:**
On a REV0 board, `flash_intel_check_vpp` sets a WARNING and returns without doing any voltage check. Control returns to `flash_intel_write_init`, which sees `WARNING != ERROR` and proceeds to drive the full write sequence with the regulator on. The user gets a single line of warning text — easy to miss in a high-volume run — and the chip is written with no actual VPP validation. For Intel 28F flash this is the same situation as on the original `eprom_check_vpp` (eprom.cpp:201-205) so the behavior is consistent, but the safety story is weak. Consider whether REV0 + Intel-flash-write should be a fail-closed combination (require FLAG_FORCE to proceed), since Intel 28F parts have a narrow VPP window (typically 12.0 V ±0.6 V) and uncalibrated REV0 supplies are known to drift.

**Fix:**
Either:
1. (Stronger) Refuse to enter the write path on REV0 unless `FLAG_FORCE` is set:
   ```cpp
   if (rurp_get_hardware_revision() == REVISION_0) {
       int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
       firestarter_response_format(response_code, "Rev0 cannot verify VPP for Intel flash");
       return;
   }
   ```
2. (Documented status quo) Leave as-is but extend the test suite with `test_flash_intel_rev0_with_force_proceeds` and a docstring noting that REV0 + Intel-flash is a knowingly unverified path.

If status quo is intended, document the safety trade-off in `01-VALIDATION.md` and leave a code comment so reviewers don't re-flag it.

---

### WR-03: `firestarter_get_data` mock reassignment after `configure_memory()` is fragile

**File:** `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp:107-109, 123, 143, 163`

**Issue:**
Every 28C test reassigns `h.firestarter_get_data = mock_get_data_scripted` after `configure_memory()` because `configure_memory()` overwrites the field with `memory_get_data` (memory.cpp:62-63). The test comment documents this as a known deviation, but the pattern is structurally brittle: if a future refactor moves any read through a different function pointer, or if `configure_memory` reassigns again deeper inside the per-protocol configure, the tests will silently regress to driving production `memory_get_data` against the no-op `rurp_read_data_buffer()` (returns 0), and **all assertions become trivially satisfied for the wrong reason** (mismatching reads against `chip_id=0` would silently "match"). The mock for `firestarter_set_control_register` is *not* reassigned, so the test exercises production `memory_set_control_register` against no-op `rurp_*` stubs — that is fine for now but couples the tests to internal dispatcher behavior.

**Fix:**
Introduce a small "post-configure mock-install" helper to centralize the rebinding and make the contract explicit:
```cpp
static void install_mocks_after_configure(firestarter_handle_t* h) {
    h->firestarter_get_data = mock_get_data_scripted;
    h->firestarter_set_data = mock_set_data;
    h->firestarter_set_control_register = mock_set_ctrl_reg;
    h->firestarter_get_control_register = mock_get_ctrl_reg;
}
```
Call this in every test immediately after `configure_memory(&h)`. The duplication today (`h.firestarter_get_data = mock_get_data_scripted` repeated four times) is also a code-smell that any future refactor will get wrong in at least one place.

Also consider asserting in the test that `firestarter_set_control_register` was *not* called with `(REGULATOR | A9_VPP_ENABLE)` still asserted after `eeprom28c_check_chip_id` returns — this would prove the regulator-clear ordering rather than relying on visual inspection.

---

### WR-04: VPP/chip-id mock state is process-global; tests are not parallel-safe

**File:** `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp:103-105, 121-123`
**File:** `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp:35-45`

**Issue:**
`s_mock_vpp_mv`, `s_mock_hw_rev`, and `s_mock_bytes` are TU-local static state. Unity runs tests sequentially in a single process and `setUp` resets them, so today this is fine. But if Unity is ever swapped for a parallel runner (some CI setups), or if these mocks get reused across suites via shared utility, the state leaks across tests. Not an active bug, just a future-proofing concern. Worth flagging because the comment in the host_stubs explicitly invites future reuse ("If a future test starts caring about register writes, the stubs can grow to record calls").

**Fix:**
Document the single-threaded contract in the host_stubs file header, or fold the mock state into a struct that's passed by pointer at setup time. Low priority.

---

### WR-05: `.gitignore` `core.*` pattern is unanchored and may match unrelated files

**File:** `firestarter/.gitignore:20-21`

**Issue:**
`core.*` is an unanchored pattern — it matches any file named `core.<something>` anywhere in the tree, including potentially intentional ones (e.g. `core.cpp`, `core.h`, `core.config`). Today the firestarter tree doesn't contain such files but the pattern over-claims. Tighter alternatives:
- `core.[0-9]*` — only numeric suffixes (PID format)
- `/core.*` — only at the firestarter repo root

**Fix:**
```
# Core dump files from native test crashes (PID-suffixed only)
core.[0-9]*
```
or
```
/core.*
```

The phase context mentions these are crash dumps from native tests; if so, they live in the repo root and the anchored form is the safer match.

## Info

### IN-01: `EEPROM_SDP_DISABLE` global is missing `static` qualifier

**File:** `firestarter/src/proms/eeprom_28c.cpp:25-32`

**Issue:**
`const byte_flip_t EEPROM_SDP_DISABLE[]` is defined at namespace scope without `static`. In C++ namespace-scope `const` defaults to internal linkage so there is no actual ODR violation, but the symbol semantics are non-obvious to readers familiar with the C convention (where the same definition would be external). Marking `static` makes the internal-only intent explicit and matches the style of the static helpers below.

**Fix:**
```cpp
static const byte_flip_t EEPROM_SDP_DISABLE[] = { ... };
```

---

### IN-02: `pgm_read_ptr` host shim casts through `void**` (technical UB)

**File:** `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h:47-49`
**File:** `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h:47-49`

**Issue:**
`#define pgm_read_ptr(addr) (*(void**)(addr))` casts through `void**` regardless of source pointer type. For a const-qualified source (e.g. `const char* const* ptr_table[]`) this strips const and is technically UB if the target is then written through. Production code only reads through this macro so no practical fault today.

**Fix:**
Use a safer cast that preserves const, or rely on `pgm_read_word` for pointer-sized reads on AVR:
```cpp
#define pgm_read_ptr(addr) (*(const void* const*)(addr))
```

Apply to both copies of the shim (or refactor to a single shared shim — see IN-03).

---

### IN-03: Duplicated `avr/pgmspace.h` and host_stubs.cpp across suites

**File:** `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h`
**File:** `firestarter/test/native/avr/test_eeprom28c_chip_id/avr/pgmspace.h`
**File:** `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp`
**File:** `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp`

**Issue:**
The two phase-01 suites carry byte-identical (or near-identical) copies of `avr/pgmspace.h` and a host_stubs.cpp that differs only in whether the VPP/HW-rev mocks are present. PlatformIO's per-test-dir source discovery requires the duplication today, but the phase context notes the "shared `test/native/avr/test_dispatch/` suite stays byte-identical" — which means three copies of this shim now exist in-tree (test_dispatch, test_flash_intel_vpp, test_eeprom28c_chip_id) and will need to drift-track on every future change. The mock variants further fragment the surface (test_eeprom28c_chip_id's host_stubs does NOT have `set_mock_vpp_mv` / `set_mock_hw_rev`; if a future test wants both, a fourth copy will appear).

**Fix:**
PlatformIO supports `extra_dirs` / shared library subdirs. Move the shim and the base `host_stubs.cpp` into a `test/native/avr/_shared/` directory (or a `test/lib/native_stubs/` library), and add per-suite TUs that only define the mockable hooks. Not blocking — this is hygiene for the next phase that needs a third or fourth native suite.

---

### IN-04: Format-specifier integer-promotion mismatch for `chip_id`

**File:** `firestarter/src/proms/flash_intel.cpp:153`
**File:** `firestarter/src/proms/eeprom_28c.cpp:63`

**Issue:**
`firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x", chip_id, handle->chip_id);` — `chip_id` and `handle->chip_id` are `uint16_t`; varargs default promotes to `int` (signed). `%x` expects `unsigned int`. Values are always non-negative so this is benign in practice, but `-Wformat` may flag it on stricter toolchains. Pre-existing style across the codebase (line 153 of flash_intel.cpp was here before this phase), only flagged because the new eeprom_28c.cpp:63 copies the same pattern.

**Fix:**
Cast explicitly:
```cpp
firestarter_response_format(response_code, "Chip ID %#04x dont match expected ID %#04x",
    (unsigned int)chip_id, (unsigned int)handle->chip_id);
```

Low priority.

---

_Reviewed: 2026-05-12T06:19:50Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
