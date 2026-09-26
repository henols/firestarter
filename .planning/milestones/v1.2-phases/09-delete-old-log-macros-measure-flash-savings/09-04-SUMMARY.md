---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 04
subsystem: native-test-stubs
tags: [logging, tests, native-stubs, dead-code-removal]
requires:
  - 09-02-atomic-legacy-deletion-and-version-bump
provides:
  - LFW-03 closed (test surface no longer references deleted production logging symbols)
affects:
  - firestarter/test/native/avr/_shared/host_stubs_common.inc
tech-stack:
  added: []
  patterns:
    - "Shared `.inc` stub aggregation pattern (Phase 6 WR-06) — the canonical edit point for native-test stub symbol surface remains the single `_shared/host_stubs_common.inc`; per-suite `host_stubs.cpp` files are pure `#include` wrappers."
key-files:
  created: []
  modified:
    - firestarter/test/native/avr/_shared/host_stubs_common.inc
key-decisions:
  - "D-03 closure: trimmed the dead LOG_*_MSG PROGMEM externs + rurp_log/rurp_log_P no-op stubs from the shared native-test stub file now that Plan 09-02 deleted the production symbols. Pure dead-code removal — no behavior change."
requirements-completed:
  - LFW-03
duration: 5 min
completed: 2026-05-19
---

# Phase 9 Plan 4: Host Stubs Trim Summary

Trimmed 27 dead lines from `firestarter/test/native/avr/_shared/host_stubs_common.inc` (8 `LOG_*_MSG` PROGMEM externs + `rurp_log`/`rurp_log_P` no-op stubs + their comment paragraphs) now that Plan 09-02 deleted the matching production symbols.

## Scope

- **Lines removed:** 27 (file went from 170 → 143 lines). The block deleted spans the original lines 42-68 (the planner's `<interfaces>` lettering called this lines 45-67 of the symbol block; the deletion also pulled in the 3-line `PROGMEM log-tag strings` comment paragraph above and the blank-line separator that followed the `rurp_log_P` block).
- **Symbols removed (10 total):**
  - 8 `LOG_*_MSG` PROGMEM externs: `LOG_OK_MSG`, `LOG_INIT_DONE_MSG`, `LOG_MAIN_DONE_MSG`, `LOG_END_DONE_MSG`, `LOG_INFO_MSG`, `LOG_DATA_MSG`, `LOG_WARN_MSG`, `LOG_ERROR_MSG`
  - 2 no-op function stubs: `rurp_log(PGM_P, const char*)`, `rurp_log_P(PGM_P, PGM_P)`
- **Untouched:** the surviving register-surface stubs from `rurp_write_to_register` onward (now at lines 42+ in the trimmed file); the `PGM_P` typedef brought in via `rurp_shield.h`; all 4 per-suite `host_stubs.cpp` files (`test_dispatch`, `test_messages`, `test_flash_intel_vpp`, `test_eeprom28c_chip_id`) — each is a pure `#include "../_shared/host_stubs_common.inc"` wrapper with no per-suite duplication.

## Verification

Plan-level acceptance gate:

| # | Criterion | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| 1 | `grep -c 'LOG_OK_MSG' ...` | 0 | 0 | PASS |
| 2 | `grep -c 'LOG_INIT_DONE_MSG\|...'` | 0 | 0 | PASS |
| 3 | `grep -E 'extern "C" void rurp_log\(|...' \| wc -l` | 0 | 0 | PASS |
| 4 | `grep -c 'rurp_write_to_register\|rurp_read_from_register'` | ≥1 | 3 | PASS |
| 5 | `pio test -e native -f '*test_dispatch*' -f '*test_messages*'` | ≥1 suite PASSED (verify-clause regex `(PASSED|22|23|24)`) | 20 test cases / 20 succeeded / both suites PASSED | PASS |
| 6 | `git diff --stat` on 4 per-suite `host_stubs.cpp` | empty | empty | PASS |

Test output:
```
=================================== SUMMARY ===================================
Environment    Test                      Status    Duration
-------------  ------------------------  --------  ------------
native         native/avr/test_dispatch  PASSED    00:00:01.977
native         native/avr/test_messages  PASSED    00:00:01.923
================= 20 test cases: 20 succeeded in 00:00:03.900 =================
```

## Commits

| Repo | Hash | Message |
|------|------|---------|
| firestarter | `ace9274` | refactor(09-04): trim dead LOG_*_MSG + rurp_log stubs from shared host stub |

Single-file deletion-only commit. No production firmware changes, no host CLI changes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Spec drift] Planner-baseline mismatch on PASS count threshold**

- **Found during:** Task 1 verification
- **Issue:** Plan body `<success_criteria>` and `<acceptance_criteria>` state "≥ 22 PASS" but the actual Phase 8 close + Plan 09-02 baseline for `pio test -e native -f '*test_dispatch*' -f '*test_messages*'` is **20 PASS** (per `<execute_plan_context>` and `09-02-SUMMARY.md`). The 22 figure in the plan body was a planner overestimate of the baseline.
- **Fix:** None needed — no production change. The plan's actual `<verify>` clause regex `(PASSED|22|23|24)` matches "PASSED" in `tail -5` of the test output and triggers on the success word, not on a specific numeric count. The plan's own acceptance gate passes; only the planner's narrative baseline was off by 2.
- **Files modified:** none
- **Verification:** `tail -5` of `pio test ...` output contains `PASSED` lines for both suites → verify-clause regex matches → acceptance passes.

**Total deviations:** 1 (planner narrative baseline drift only; no production / no test count regression). **Impact:** none — both native test suites remain fully green at the actual baseline (20/20 PASS unchanged from Plan 09-02 close).

## Authentication Gates

None.

## Issues Encountered

None.

## Threat Flags

None — the trim removes dead-stub material only. The threat register's `mitigate` items (T-09-04-01: link-failure ordering, T-09-04-02: over-deletion of surviving stubs) are both verified clean by the static greps + native test pass. T-09-04-03 (comment-only references to `rurp_log` in the 4 sibling `avr/pgmspace.h` shim files) remains `accept` per the plan — those files are untouched and the comments are informational, not declarative.

## Self-Check: PASSED

- File `firestarter/test/native/avr/_shared/host_stubs_common.inc` exists on disk: PASS (143 lines, down from 170).
- Commit `ace9274` exists in `firestarter` sub-repo `git log`: PASS.
- All 6 plan acceptance criteria verified above: PASS.
- Plan-level `<verification>` block (4 gates: LOG_*_MSG=0, rurp_log defs=0, surviving stubs present, native tests green): PASS — PLAN 04 GREEN.

## Next

Phase 9 has plans 01, 02, 04 closed. Per `09-CONTEXT.md` decision graph, the remaining Phase 9 work (flash-savings measurement / LFW-04) continues with the next plan in the phase queue.
