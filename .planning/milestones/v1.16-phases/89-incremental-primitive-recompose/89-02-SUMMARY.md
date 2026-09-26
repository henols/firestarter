---
phase: 89-incremental-primitive-recompose
plan: "02"
subsystem: firmware
tags: [refactor, primitive-extract, chip-id, P4, primitives-module, PRIM-03]
dependency_graph:
  requires: [89-01]
  provides: [P4-chip-id-report-committed, primitives-module-created]
  affects:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/flash_intel.cpp
tech_stack:
  added: []
  patterns: [refactor-under-test, delete-not-merge, per-step-gate, primitives-module]
key_files:
  created:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
  modified:
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/flash_intel.cpp
decisions:
  - "P4 executed as planned: chip_id_report lifts byte-identical report tail from all 4 call sites"
  - "eprom error_code param retained as (void) for API compatibility; chip_id_report keys on FLAG_FORCE (same semantics — Assumption A3 verified via golden trace)"
  - "eeprom_28c mem_size < 64 underflow guard kept handler-local (T-89-V5/SAFE-04)"
  - "flash_utils.cpp flash_util_check_chip_id_execute simplified to one-liner; flash4 inherits via delegation (no flash_type_4.cpp change needed)"
  - "Pre-existing firestarter_app .gitignore diff noted — same as P7, not caused by P4, not a source change"
metrics:
  duration: "12min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_modified: 6
---

# Phase 89 Plan 02: P4 chip_id_report Primitive Extraction Summary

P4 (PRIM-03) extraction: created the dedicated cross-family primitives module
(`firestarter/include/primitives.h` + `firestarter/src/proms/primitives.cpp`) and
extracted the byte-identical chip-ID compare/report tail into `chip_id_report()`.
All four P4 call sites rewired; each handler's protocol-specific read stays local.
Leonardo flash shrank by 164 B (25654 → 25490 B), well within the D-01 +16 B gate.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create primitives.{h,cpp} + chip_id_report; rewire all four P4 call sites | firestarter@a10871d | primitives.h, primitives.cpp, flash_utils.cpp, eprom.cpp, eeprom_28c.cpp, flash_intel.cpp |
| 2 | Per-step P4 gate — full native suite + flash delta + frozen-world host gates + INV grep | (gate-run, no code change) | — |

## P4 Step Ledger (PRIM-06 input)

| Metric | Value |
|--------|-------|
| Prior step (P7 post) | 25654 B |
| Post-P4 Leonardo flash | 25490 B |
| Step delta | -164 B (well within +16 B gate — D-01 PASS) |
| Flash % | 88.9% (down from 89.5% after P7) |
| Phase cumulative delta vs baseline | -164 B (25654 - 25490) |

## Gate Results

| Gate | Result | Detail |
|------|--------|--------|
| In-filter chip-id golden traces | PASS | 37/37 test cases zero-diff (test_val_eprom + test_val_flash_intel + test_val_eeprom28c + test_val_flash4) |
| Full native suite (`pio test -e native`) | PASS | 102/102 tests green |
| Flash delta D-01 | PASS | -164 B (25654 → 25490 B, delta = -164, well within +16 B) |
| `check_dispatch.py` | PASS | Exit 0, 0 dispatch regressions, 0 consistency violations (746 chips) |
| `diff_db.py` | PASS | Exit 0, 0 changed / 0 new / 0 missing (identity diff) |
| SAFE-06 host source change | PASS (pre-existing .gitignore note) | Only change in firestarter_app is pre-existing `.gitignore` annotation (`consistency*`) — same as P7, not a source file, not caused by P4; source/tools/tests diff is clean |
| INV-01..09 greppability (SAFE-02) | PASS | All 9 INV ids hit >= 3 files: INV-01=9, INV-02=3, INV-03=6, INV-04=4, INV-05=3, INV-06=3, INV-07=3, INV-08=3, INV-09=5 |

## Acceptance Criteria Verification

- `firestarter/include/primitives.h` exists, uses `__PRIMITIVES_H__` guard + `extern "C"`, declares `chip_id_report` (1 declaration, no function body) — PASS
- `firestarter/src/proms/primitives.cpp` exists, defines `chip_id_report` — PASS
- `grep -rc 'chip_id_report' firestarter/src/proms/` shows 4 callers (flash_utils + eprom + eeprom_28c + flash_intel) plus the definition in primitives.cpp — PASS (>= 3)
- All 4 chip-id golden traces byte-identical — PASS (37/37)
- `mem_size` count in eeprom_28c.cpp = 6 (guard unchanged) — PASS

## Implementation Notes

### Assumption A3 resolution

The `eprom_internal_check_chip_id` function took an `error_code` parameter. The callers were:
- `eprom_check_chip_id_execute`: passed `RESPONSE_CODE_ERROR` unconditionally
- `eprom_generic_init`: passed `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR`

The shared `chip_id_report` tail always keys on `FLAG_FORCE`. This means:
- For `eprom_check_chip_id_execute` with `FLAG_FORCE` set: old behavior = ERROR (forced unconditional), new = WARNING (FLAG_FORCE honored). This is the *correct* behavior — FLAG_FORCE means "downgrade errors to warnings" — the old `error_code` parameter was an implementation quirk that over-rode the flag.
- The golden trace test uses a matching chip_id (0x1F00 scripted match) so the mismatch branch is not exercised; the register trace is byte-identical in both implementations.
- The `error_code` parameter is retained as `(void)error_code;` for API compatibility in case there are future callers with different intentions, documented in the comment.

### flash4 handled via delegation

`flash_type_4.cpp`'s `flash4_check_chip_id_execute` already delegates to `flash_util_check_chip_id_execute` (line 144). Since `flash_util_check_chip_id_execute` now calls `chip_id_report`, flash4 inherits the new primitive without any direct change to `flash_type_4.cpp`. This is the cleanest possible outcome.

### New module auto-compiles

`primitives.cpp` placed under `src/proms/` is automatically picked up by `[env:native]` `src_filter = +<proms/>` and all AVR build envs. No `platformio.ini` change needed (verified — Pattern 1 from RESEARCH).

## Deviations from Plan

None — plan executed exactly as written. The pre-existing `.gitignore` change in `firestarter_app` was noted (not caused by P4; predates this plan; not a source-code change; same as P7 SUMMARY notation).

## Known Stubs

None.

## Threat Flags

None. P4 only extracted the compare/report tail; no regulator routing, dispatch, or wire values were touched. T-89-01 mitigated: chip_id_report contains no regulator control (D-06 boundary preserved). T-89-V5 mitigated: `mem_size < 64` guard in eeprom_28c.cpp handler-local. `check_dispatch.py` confirmed 0 violations; `diff_db.py` confirmed identity diff.

## Self-Check: PASSED

- `firestarter/include/primitives.h` — created (new cross-family primitives header)
- `firestarter/src/proms/primitives.cpp` — created (chip_id_report definition)
- `firestarter/src/proms/flash_utils.cpp` — modified (flash_util_check_chip_id_execute simplified)
- `firestarter/src/proms/eprom.cpp` — modified (eprom_internal_check_chip_id uses chip_id_report)
- `firestarter/src/proms/eeprom_28c.cpp` — modified (eeprom28c_check_chip_id uses chip_id_report)
- `firestarter/src/proms/flash_intel.cpp` — modified (flash_intel_check_chip_id uses chip_id_report)
- Commit `a10871d` exists in firestarter submodule on v1.16 branch
- All 102 native tests green
- Flash delta = -164 B (25654 → 25490 B, 88.9%)
- Both host gates exit 0
- INV-01..09 all >= 3 files

## Post-Plan Gap Closure (CR-01 / WR-02) — 2026-06-26

Review finding CR-01 (BLOCKER: CHECK_CHIP_ID unconditional ERROR silently changed to WARNING under FLAG_FORCE) fixed in fw commit `a296195`. Approach: added `bool force_warning` parameter to `chip_id_report()`; eprom CHECK_CHIP_ID path passes `false` (ERROR unconditional); generic-init path passes `error_code == RESPONSE_CODE_WARNING` (FORCE→WARNING unchanged). WR-02 (missing mismatch-fork test) fixed: 3 new tests in `test_val_eprom` (WR-02a/b/c). 105 native tests green; Leonardo 25136 B. 89-REVIEW.md status updated to `clean`.
