---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: 01
subsystem: firmware
tags: [vpp-skip, eprom, native-test, tdd, d11, fix01]
dependency_graph:
  requires: []
  provides: [firmware-vpp-skip-gate, native-dispatch-vpp-tests]
  affects: [eprom.cpp, test_configure_memory.cpp, host_stubs.cpp]
tech_stack:
  added: []
  patterns: [operation-type-keyed-guard, response_code-observable-test]
key_files:
  created: []
  modified:
    - firestarter/src/proms/eprom.cpp
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/test/native/avr/test_dispatch/host_stubs.cpp
decisions:
  - "Observable for VPP-skip tests: response_code after firestarter_operation_init (WARNING=2 when VPP check ran with 0 mV stub, OK=1 when skipped) — cleaner than recording control-register calls through the ep_set_control_register static, which proved difficult to observe from test context"
  - "HOST_STUBS_CUSTOM_HW_REVISION added to host_stubs.cpp returning REVISION_1 (1): the default stub returns REVISION_0 (0), triggering an early-return in eprom_check_vpp before the regulator-enable, making positive VPP tests vacuously pass"
  - "delay() ArduinoFake stub added to setUp(): eprom_check_vpp calls delay(100) which is a FakeIt virtual method; unstubbed it throws UnexpectedMethodCallException"
  - "D-11 guard placed as early-return in eprom_generic_init before eprom_check_vpp: cleanest choke point, no new flag bit, uses existing CMD_READ/CMD_BLANK_CHECK constants"
  - "CMD_CHECK_CHIP_ID explicitly NOT added to the skip guard (needs 12V on A9 for chip-ID; verified by negative test)"
metrics:
  duration: 12 minutes
  completed_date: "2026-06-25"
  tasks: 3
  files_modified: 3
---

# Phase 84 Plan 01: D-11 VPP-Skip Firmware Gate Summary

**One-liner:** Operation-type-keyed VPP-skip in `eprom_generic_init` — CMD_READ/CMD_BLANK_CHECK skip `eprom_check_vpp` entirely (clears chip-1 18.8V read refusal + benign low warnings); write/erase/chip-id still gate VPP; proven by 5-assertion native dispatch test (2 positive + 3 negative).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create firmware v1.15 branch + RED native dispatch tests | c480d3f | test_configure_memory.cpp, host_stubs.cpp |
| 2 | Implement D-11 VPP-skip in eprom_generic_init (GREEN) | cb947c7 | eprom.cpp |
| 3 | Confirm Leonardo build fit (flash ≤ ~90%) | — (no source change) | — |

## Key Results

### Firmware Branch

- Branch: `v1.15-bench-validation-of-operator-inventory` off beta HEAD `a1953c2` (b10)
- Forked BEFORE the firmware edit per D-12 (Pitfall 6 avoided)
- Meta gitlink stays pinned at `a1953c2` (operator-gated beta cut)

### Native Dispatch Test Suite

**Result: 87/87 PASSED** (full native suite green)

VPP-skip gate group (5 new tests in `test_configure_memory.cpp`):

| Test | Type | Before fix | After fix |
|------|------|-----------|-----------|
| `test_eprom_read_does_not_run_vpp_check` | Positive (D-11) | FAIL (WARNING set) | PASS (OK) |
| `test_eprom_blank_check_does_not_run_vpp_check` | Positive (D-11) | FAIL (WARNING set) | PASS (OK) |
| `test_eprom_write_still_runs_vpp_check` | Negative (T-84-01) | PASS | PASS |
| `test_eprom_erase_still_runs_vpp_check` | Negative (T-84-01) | PASS | PASS |
| `test_eprom_check_chip_id_still_runs_vpp_check` | Negative (T-84-01) | PASS | PASS |

### Leonardo Flash Usage (Task 3 — D-10 fit gate)

```
Flash: [========= ]  89.5% (used 25666 bytes from 28672 bytes)
RAM:   [========  ]  78.1% (used 1999 bytes from 2560 bytes)
```

**89.5% ≤ ~90% gate: PASSED**. The VPP-skip change added 6 lines to `eprom_generic_init` (guard + early-return). Flash headroom is tight but within bounds — the gate is clear. This is the pre-condition for Plan 84-05's bench re-flash.

### Implementation Details

The guard in `eprom_generic_init` (`eprom.cpp`):

```cpp
void eprom_generic_init(firestarter_handle_t* handle) {
    /* D-11 (Phase 84): read and blank-check do not drive VPP — skip the
     * regulator-enable + measurement + ERROR/WARNING.  Write/erase/chip-id
     * still gate VPP exactly as before (T-84-01 over-voltage block intact). */
    if (handle->cmd == CMD_READ || handle->cmd == CMD_BLANK_CHECK) {
        return;
    }
    eprom_check_vpp(handle);
    ...
}
```

- Uses existing `CMD_READ` (1) and `CMD_BLANK_CHECK` (4) constants — no new flag bit (A4 confirmed)
- `eprom_check_vpp` is NOT modified — write/erase/chip-id still call it through unchanged paths
- `firestarter.h` unchanged — host↔firmware constant parity preserved (CLAUDE.md)
- No `eprom_operations.py` edit required (host does not run its own VPP gate)

### Test Infrastructure Changes

**host_stubs.cpp** (`HOST_STUBS_CUSTOM_HW_REVISION`):
- Default stub returns `REVISION_0 = 0` → early return in `eprom_check_vpp` before regulator-enable
- Override returns `REVISION_1 = 1` → full VPP path executes (regulator-enable + measurement + error/warning)
- Only affects new VPP-skip tests (existing dispatch tests never call `firestarter_operation_init`)

**test_configure_memory.cpp** (setUp stub extension):
- Added `When(Method(ArduinoFake(), delay)).AlwaysReturn()` — `eprom_check_vpp` calls `delay(100)` which is a FakeIt virtual method; unstubbed it throws `UnexpectedMethodCallException`
- Additive-only; existing 18 tests unaffected (they never call `firestarter_operation_init`)

**Observable choice**: `response_code` after calling `firestarter_operation_init`:
- VPP check ran with 0 mV stub + 12000 mV target: `0 < 12000*95/100=11400` → `RESPONSE_CODE_WARNING (2)`
- VPP check skipped (D-11 guard): `response_code` stays `RESPONSE_CODE_OK (1)`
- This observable is simpler and more reliable than trying to intercept `ep_set_control_register` (file-scope static in eprom.cpp)

## Deviations from Plan

**1. [Rule 1 - Bug] Recording stub observable changed from control-register count to response_code**

- **Found during:** Task 1 RED verification
- **Issue:** Initial design used a recording `firestarter_set_control_register` function to count CTRL_VPP_REGULATOR_ENABLE calls via `ep_set_control_register`. The positive tests (CMD_READ/CMD_BLANK_CHECK) vacuously passed (count=0) because: (a) the default hardware-revision stub returned REVISION_0, causing early return BEFORE the regulator-enable call; (b) even after fixing (a), ArduinoFake threw `UnexpectedMethodCallException` for `delay()` (an unstubbed FakeIt virtual method).
- **Fix:** Two infrastructure fixes: (1) override `HOST_STUBS_CUSTOM_HW_REVISION` in host_stubs.cpp; (2) stub `delay()` in setUp(). Then switched observable to `response_code` (simpler, no need for the ep_set_control_register capture chain). The final test design is cleaner than the original control-register-count approach and more directly proves the behavioral invariant (VPP check ran vs. skipped).
- **Files modified:** test_configure_memory.cpp, host_stubs.cpp
- **Commits:** c480d3f

## Verification Results

- `git -C firestarter rev-parse --abbrev-ref HEAD` → `v1.15-bench-validation-of-operator-inventory` ✓
- `pio test -e native` → 87/87 PASSED ✓
- Positive skip assertions (CMD_READ/CMD_BLANK_CHECK): GREEN after fix ✓
- Negative still-gate assertions (CMD_WRITE/CMD_ERASE/CMD_CHECK_CHIP_ID): GREEN before AND after fix ✓
- `grep -n "CMD_READ" firestarter/src/proms/eprom.cpp` → line 294 guard present ✓
- `grep -c "CMD_CHECK_CHIP_ID" firestarter/src/proms/eprom.cpp` → 1 (not added to skip) ✓
- `diff HEAD~2..HEAD -- firestarter/include/firestarter.h` → no changes (no new flag bit) ✓
- `pio run -e leonardo` → EXIT 0, Flash 89.5% ≤ ~90% ✓
- Meta gitlink NOT staged/committed ✓

## Success Criteria Assessment

- [x] D-11 VPP-skip implemented and proven by native dispatch test (FIX-01 firmware half)
- [x] Over-voltage block preserved for write/erase/chip-id (T-84-01 mitigated, 3 negative tests)
- [x] Build is bench-flashable (D-10 fit gate 89.5%), enabling 84-05 re-flash + 2516 re-read
- [x] Firmware on v1.15 branch (not beta), meta gitlink pinned (D-12 / standing policy)
- [x] No new flag bit / constant (host↔firmware parity preserved, CLAUDE.md)

## Bench Precondition (84-05 Re-flash)

- Branch: `v1.15-bench-validation-of-operator-inventory` at commit `cb947c7`
- Flash budget: 89.5% (25666 / 28672 bytes)
- The build `.pio/build/leonardo/firestarter_leonardo.hex` is ready for `pio run -t upload -e leonardo`

## Self-Check: PASSED

- `firestarter/src/proms/eprom.cpp` exists and contains CMD_READ guard at line 294 ✓
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` contains `test_eprom_read_does_not_run_vpp_check` ✓
- `git -C /workspaces/firestarter log --oneline` shows commits `cb947c7` (feat) and `c480d3f` (test) on the v1.15 branch ✓
- 87/87 native tests pass ✓
